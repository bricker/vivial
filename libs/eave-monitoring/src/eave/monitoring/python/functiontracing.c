#include <Python.h>
#include <frameobject.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <pthread.h>
#include <stdio.h>
#include <stdbool.h>
#include <unistd.h>

#include "mpack/mpack.h"

//#include <assert.h>
// By default, python c extensions compile with asserts disable and it is not
// super easy to disable this behavior (AFAIK). Use this custom assert for now.
void assert_helper(int lineno, char* expr) {
    printf("Assertion failed on line %d: %s\n", lineno, expr);
    exit(-1);
}
#undef assert
#define assert(expr) \
    if (!(expr)) \
        assert_helper(__LINE__, #expr)

////////////////////////////////////////////////////////////////////////////////
// Types
////////////////////////////////////////////////////////////////////////////////
typedef struct {
    // The name of the module being hooked
    const char* module;
    // The function overridden by this hook
    PyObject*   original;
    // The definition for this hook
    PyMethodDef fn;
} HookedFunction;

// I don't like the default name.
typedef struct timespec Timestamp;

typedef mpack_writer_t Writer;

// Storage specific to each thread used for buffering/transmitting data.
typedef struct {
    // The socket this thread is writing to.
    intptr_t socket;

    // Our output buffer.  This is passed to messagepack and may only be
    // touched by it.
    char   buffer[1 << 17];

    // The messagepack writer for the current thread.
    Writer writer;
} ThreadState;

////////////////////////////////////////////////////////////////////////////////
// Prototypes
////////////////////////////////////////////////////////////////////////////////
static Writer* Fprofile_Writer(void);
static void    Mpack_Flush(Writer* writer, const char* buffer, size_t bytes);

static Timestamp Fprofile_Time(void);

static PyObject*    Fprofile_StartTrace(PyObject* obj, PyObject* args, PyObject* kwargs);
static PyObject*    Fprofile_Terminate(void);
static ThreadState* Fprofile_CreateThreadState(void);
static void         Fprofile_ResetThreadState(void);
static void         Fprofile_ThreadTeardown(void* key);

static PyObject* Fprofile_ConfigEnableMemoryTracing(void);

static void Fprofile_HookFunctions(void);
static void Fprofile_RecordAllocations(void);

static int       Fprofile_FunctionTrace(PyObject* obj, PyFrameObject* frame, int what, PyObject* arg);
static PyObject* Fprofile_ThreadFunctionTrace(PyObject* obj, PyFrameObject* frame, int what, PyObject* arg);
static PyObject* Fprofile_LoggingHook(HookedFunction* hook, PyObject* args, PyObject* kwargs);
static PyObject* Fprofile_ImportHook(HookedFunction* hook, PyObject* args, PyObject* kwargs);
static PyObject* Fprofile_MpexitHook(HookedFunction* hook, PyObject* args, PyObject* kwargs);

#define DIM(x) (sizeof(x) / sizeof(x[0]))

////////////////////////////////////////////////////////////////////////////////
// Globals
////////////////////////////////////////////////////////////////////////////////
// This key is used to fetch the thread local instance of the "ThreadState"
// structure. Each thread must have its own instance of output buffer, for
// example.
static pthread_key_t Tss_Key = 0;

// Various global configuration for this module, some of which is exposed to
// Python via module methods.
static struct {
    // True iff we should enable tracing memory allocations.  This may be very
    // expensive, so is disabled unless explicitly requested.
    bool enableMemoryTracing;

    // True iff we've started tracing and haven't been marked as terminated.
    // When this is set, we're allowed to send messages to the profile
    // generation server.
    bool started;

    // The first 64 characters of the argv (NUL terminated) that Python was
    // invoked with.
    // NOTE: This length limit is arbitrary, but it is displayed in the GUI so
    // it should probably not be super large.
    char argv[64];

    // Force messages to be flushed immediately.
    // NOTE: This will add significant overhead on OSes/hardware with expensive
    // context switches, but may be useful for debugging and is temporarily
    // being used when we're in a forked context.
    bool immediateFlushes;

    // Our PID.
    pid_t pid;

    // The Unix socket address we're using to communicate with the profile
    // server.
    struct sockaddr_un socket;
} moduleConfiguration;

// The set of methods exposed by this module to Python.
enum {
    METHOD_STARTTRACE,
    METHOD_CONFIG_TRACEMEM,
    METHOD_FUNCTIONTRACE,
    METHOD_TERMINATE,
    METHOD_END
};
static PyMethodDef methods[] = {
    [METHOD_STARTTRACE] = {
        .ml_name  = "begin_tracing",
        .ml_meth  = (PyCFunction) Fprofile_StartTrace,
        .ml_flags = METH_VARARGS,
        .ml_doc   = "Initializes Fprofile's tracing sequence."
    },
    [METHOD_CONFIG_TRACEMEM] = {
        .ml_name  = "config_tracememory",
        .ml_meth  = (PyCFunction) Fprofile_ConfigEnableMemoryTracing,
        .ml_flags = METH_NOARGS,
        .ml_doc   = "Enables memory tracing for Fprofile."
    },
    [METHOD_FUNCTIONTRACE] = {
        .ml_name  = "_function_trace",
        .ml_meth  = (PyCFunction) Fprofile_ThreadFunctionTrace,
        .ml_flags = METH_VARARGS,
        .ml_doc   = "INTERNAL USE ONLY"
    },
    [METHOD_TERMINATE ] = {
        .ml_name  = "terminate",
        .ml_meth  = (PyCFunction) Fprofile_Terminate,
        .ml_flags = METH_NOARGS,
        .ml_doc   = "Stop profiling events.  Mainly called internally."
    },
    [METHOD_END] = {NULL, NULL, 0, NULL}
};

////////////////////////////////////////////////////////////////////////////////
// Server Communication
////////////////////////////////////////////////////////////////////////////////

static Writer* Fprofile_Writer(void) {
    assert(Tss_Key != 0);

    if (!moduleConfiguration.started) {
        // We aren't running (either starting up or shutting down), so
        // shouldn't write anything.
        return NULL;
    }

    // Fetch the ThreadState for the current thread.  It's created as late as
    // the first function call for the thread, so we can plausibly get messages
    // before having anywhere to store/send them to.  Drop them if so - they
    // weren't too important if we aren't running code yet.
    ThreadState* state = pthread_getspecific(Tss_Key);
    if (state == NULL) {
        // The thread hasn't officially started yet, so drop this message.
        return NULL;
    }

    return &state->writer;
}

static void Mpack_Flush(Writer* writer, const char* buffer, size_t bytes) {
    // The context passed to Mpack is the socket to send on.
    intptr_t socket = (intptr_t) writer->context;

    if (send(socket, buffer, bytes, 0) == -1) {
        perror("send failed");
        exit(-1);
    }
}

////////////////////////////////////////////////////////////////////////////////
// Misc
////////////////////////////////////////////////////////////////////////////////
static inline Timestamp Fprofile_Time(void) {
    // This effectively fetches the output of RDTSC, making it quick but not
    // very useful on its own, as there is no meaningful epoch for the time.
    Timestamp tsc = { 0 };
    clock_gettime(CLOCK_MONOTONIC, &tsc);
    return tsc;
}

// Given a PyObject (likely `co_name` or similar), return a UTF-8
// representation.
static inline const char* Fprofile_UnicodeToUtf8(PyObject* obj) {
    if (obj == NULL) {
        return "<NULL>";
    }

    if (PyUnicode_Check(obj)) {
        const char* utf8 = PyUnicode_AsUTF8(obj);

        return utf8 != NULL ? utf8 : "<DECODE ERROR>";
    } else if (obj == Py_None) {
        return "<NONE>";
    } else {
        return "<UNKNOWN>";
    }
}

////////////////////////////////////////////////////////////////////////////////
// Function Hooking
////////////////////////////////////////////////////////////////////////////////
// Generate a function capable of overriding an existing Python function, and
// attach enough information about the original function to call it.
// NOTE: These must live forever, as Python requires them to call the
// underlying C function.

#define HOOK_METHOD(id, module, name, hook)                    \
    static PyObject* hooked_function_##id(PyObject* s,         \
            PyObject* args, PyObject* kwargs);                 \
    static HookedFunction hooked_function_info_##id = {        \
        module,                                                \
        NULL,                                                  \
        {                                                      \
            name,                                              \
            (PyCFunction) hooked_function_##id,                \
            METH_VARARGS | METH_KEYWORDS,                      \
            NULL                                               \
        }                                                      \
    };                                                         \
    static PyObject* hooked_function_##id(PyObject* s,         \
            PyObject* args, PyObject* kwargs) {                \
        return hook(&hooked_function_info_##id, args, kwargs); \
    }

#define HOOK_ENTRY(id) \
    &hooked_function_info_##id

// Generate the various hooking functions we need.
HOOK_METHOD(0, "logging", "debug",                        Fprofile_LoggingHook)
HOOK_METHOD(1, "logging", "log",                          Fprofile_LoggingHook)
HOOK_METHOD(2, "logging", "info",                         Fprofile_LoggingHook)
HOOK_METHOD(3, "logging", "warning",                      Fprofile_LoggingHook)
HOOK_METHOD(4, "logging", "error",                        Fprofile_LoggingHook)
HOOK_METHOD(5, "logging", "critical",                     Fprofile_LoggingHook)
HOOK_METHOD(6, "logging", "fatal",                        Fprofile_LoggingHook)
HOOK_METHOD(7, "logging", "exception",                    Fprofile_LoggingHook)
HOOK_METHOD(8, "builtins", "print",                       Fprofile_LoggingHook)
HOOK_METHOD(9, "builtins", "__import__",                  Fprofile_ImportHook)
HOOK_METHOD(10, "multiprocessing.util", "_exit_function", Fprofile_MpexitHook)

// Register the hooked functions
static HookedFunction* hooks[] = {
    HOOK_ENTRY(0),
    HOOK_ENTRY(1),
    HOOK_ENTRY(2),
    HOOK_ENTRY(3),
    HOOK_ENTRY(4),
    HOOK_ENTRY(5),
    HOOK_ENTRY(6),
    HOOK_ENTRY(7),
    HOOK_ENTRY(8),
    HOOK_ENTRY(9),
    HOOK_ENTRY(10)
};

// Register the hooks we've created.
static void Fprofile_HookFunctions(void) {
    for (size_t i = 0; i < DIM(hooks); i++) {
        HookedFunction* hook = hooks[i];

        // We need to import the target modules before hooking them.
        PyObject* module = PyImport_ImportModule(hook->module);

        // Retrieve the original function and store it so we can call it from
        // the hook.
        hook->original = PyObject_GetAttrString(module, hook->fn.ml_name);

        // Override the original function with our hook.
        PyObject* wrapper  = PyCFunction_New(&hook->fn, module);
        PyObject_SetAttrString(module, hook->fn.ml_name, wrapper);
        Py_DECREF(wrapper);
        Py_DECREF(module);
    }
}

////////////////////////////////////////////////////////////////////////////////
// Allocator
////////////////////////////////////////////////////////////////////////////////
static PyMemAllocatorEx logging_allocator[3] = { 0 };
static PyMemAllocatorEx original_allocator[3] = { 0 };

static void* logging_malloc(void* ctx, size_t size) {
    Timestamp            tsc    = Fprofile_Time();
    PyMemAllocatorDomain domain = (PyMemAllocatorDomain) ctx;
    PyMemAllocatorEx*    alloc  = &original_allocator[domain];
    Writer*              writer = Fprofile_Writer();

    void* addr = alloc->malloc(alloc->ctx, size);

    if (writer != NULL) {
        mpack_start_array(writer, 3);
        mpack_write_cstr(writer, "Allocation");

        mpack_start_array(writer, 2);
        mpack_write_u32(writer, tsc.tv_sec);
        mpack_write_u32(writer, tsc.tv_nsec);
        mpack_finish_array(writer);

        mpack_start_array(writer, 3);
        mpack_write_cstr(writer, "Alloc");
        mpack_write_u64(writer, size);
        mpack_write_u64(writer, (uintptr_t) addr);
        mpack_finish_array(writer);
        mpack_finish_array(writer);

        if (moduleConfiguration.immediateFlushes) {
            mpack_writer_flush_message(writer);
        }
    }

    return addr;
}

static void* logging_calloc(void* ctx, size_t nelem, size_t elsize) {
    Timestamp            tsc    = Fprofile_Time();
    PyMemAllocatorDomain domain = (PyMemAllocatorDomain) ctx;
    PyMemAllocatorEx*    alloc  = &original_allocator[domain];
    Writer*              writer = Fprofile_Writer();

    void* addr = alloc->calloc(alloc->ctx, nelem, elsize);

    if (writer != NULL) {
        mpack_start_array(writer, 3);
        mpack_write_cstr(writer, "Allocation");

        mpack_start_array(writer, 2);
        mpack_write_u32(writer, tsc.tv_sec);
        mpack_write_u32(writer, tsc.tv_nsec);
        mpack_finish_array(writer);

        mpack_start_array(writer, 3);
        mpack_write_cstr(writer, "Alloc");
        mpack_write_u64(writer, nelem * elsize);
        mpack_write_u64(writer, (uintptr_t) addr);
        mpack_finish_array(writer);
        mpack_finish_array(writer);

        if (moduleConfiguration.immediateFlushes) {
            mpack_writer_flush_message(writer);
        }
    }

    return addr;
}

static void* logging_realloc(void* ctx, void* old_addr, size_t new_size) {
    Timestamp            tsc    = Fprofile_Time();
    PyMemAllocatorDomain domain = (PyMemAllocatorDomain) ctx;
    PyMemAllocatorEx*    alloc  = &original_allocator[domain];
    Writer*              writer = Fprofile_Writer();

    void* new_addr = alloc->realloc(alloc->ctx, old_addr, new_size);

    if (writer != NULL) {
        mpack_start_array(writer, 3);
        mpack_write_cstr(writer, "Allocation");

        mpack_start_array(writer, 2);
        mpack_write_u32(writer, tsc.tv_sec);
        mpack_write_u32(writer, tsc.tv_nsec);
        mpack_finish_array(writer);

        mpack_start_array(writer, 4);
        mpack_write_cstr(writer, "Realloc");
        mpack_write_u64(writer, new_size);
        mpack_write_u64(writer, (uintptr_t) old_addr);
        mpack_write_u64(writer, (uintptr_t) new_addr);
        mpack_finish_array(writer);
        mpack_finish_array(writer);

        if (moduleConfiguration.immediateFlushes) {
            mpack_writer_flush_message(writer);
        }
    }

    return new_addr;
}

static void logging_free(void* ctx, void* old_addr) {
    if (old_addr == NULL) {
        // Abort quickly.
        return;
    }

    Timestamp            tsc    = Fprofile_Time();
    PyMemAllocatorDomain domain = (PyMemAllocatorDomain) ctx;
    PyMemAllocatorEx*    alloc  = &original_allocator[domain];
    Writer*              writer = Fprofile_Writer();

    alloc->free(alloc->ctx, old_addr);

    if (writer != NULL) {
        mpack_start_array(writer, 3);
        mpack_write_cstr(writer, "Allocation");

        mpack_start_array(writer, 2);
        mpack_write_u32(writer, tsc.tv_sec);
        mpack_write_u32(writer, tsc.tv_nsec);
        mpack_finish_array(writer);

        mpack_start_array(writer, 2);
        mpack_write_cstr(writer, "Free");
        mpack_write_u64(writer, (uintptr_t) old_addr);
        mpack_finish_array(writer);
        mpack_finish_array(writer);

        if (moduleConfiguration.immediateFlushes) {
            mpack_writer_flush_message(writer);
        }
    }
}

static void Fprofile_RecordAllocations(void) {
    const PyMemAllocatorDomain domains[] = {
        PYMEM_DOMAIN_RAW,
        PYMEM_DOMAIN_MEM,
        PYMEM_DOMAIN_OBJ,
    };

    // Shouldn't be recording allocations if we weren't asked to.
    assert(moduleConfiguration.enableMemoryTracing);

    // Hook the allocators
    for (size_t i = 0; i < DIM(domains); i++) {
        PyMemAllocatorDomain domain = domains[i];

        // Fetch the original allocator and store it so we can call into it.
        PyMem_GetAllocator(domain, &original_allocator[domain]);

        // Setup a new allocator that wraps the old one.
        logging_allocator[domain] = (PyMemAllocatorEx) {
            .ctx = (void*) domain,
            .malloc = &logging_malloc,
            .calloc = &logging_calloc,
            .realloc = &logging_realloc,
            .free = &logging_free,
        };
        PyMem_SetAllocator(domain, &logging_allocator[domain]);
        // This can happen if this function is called multiple times and would create
        // an infinite loops upon allocation.
        assert(original_allocator[domain].malloc != logging_allocator[domain].malloc);
    }
}

////////////////////////////////////////////////////////////////////////////////
// Callbacks
////////////////////////////////////////////////////////////////////////////////
static int Fprofile_FunctionTrace(PyObject* obj, PyFrameObject* frame, int what, PyObject* arg) {
    PyCFunctionObject* fn = (PyCFunctionObject*) arg;
    Timestamp tsc = Fprofile_Time();

    Writer* writer = Fprofile_Writer();
    if (writer == NULL) {
        return 0;
    }

    switch (what) {
        case PyTrace_CALL:
            mpack_start_array(writer, 5);
            mpack_write_cstr(writer, "Call");

            mpack_start_array(writer, 2);
            mpack_write_u32(writer, tsc.tv_sec);
            mpack_write_u32(writer, tsc.tv_nsec);
            mpack_finish_array(writer);

            {
                // TODO: Check if frame is none or similar
#if PY_VERSION_HEX >= 0x030a00a0
                // Python >= 3.10 should use the standard accessors
                PyCodeObject* code = PyFrame_GetCode(frame);
                int lineno = PyFrame_GetLineNumber(frame);
#else
                PyCodeObject* code = frame->f_code;
                int lineno = frame->f_lineno;
#endif

#if PY_VERSION_HEX >= 0x030b00a0
                mpack_write_cstr(writer, Fprofile_UnicodeToUtf8(code->co_qualname));
#else
                mpack_write_cstr(writer, Fprofile_UnicodeToUtf8(code->co_name));
#endif
                mpack_write_cstr(writer, Fprofile_UnicodeToUtf8(code->co_filename));
                mpack_write_u32(writer, lineno);

#if PY_VERSION_HEX >= 0x030a00a0
                Py_DECREF(code);
#endif
            }
            mpack_finish_array(writer);
            break;
        case PyTrace_RETURN:
            mpack_start_array(writer, 3);
            mpack_write_cstr(writer, "Return");

            mpack_start_array(writer, 2);
            mpack_write_u32(writer, tsc.tv_sec);
            mpack_write_u32(writer, tsc.tv_nsec);
            mpack_finish_array(writer);

            {
#if PY_VERSION_HEX >= 0x030a00a0
                PyCodeObject* code = PyFrame_GetCode(frame);
#else
                PyCodeObject* code = frame->f_code;
#endif
#if PY_VERSION_HEX >= 0x030b00a0
                mpack_write_cstr(writer, Fprofile_UnicodeToUtf8(code->co_qualname));
#else
                mpack_write_cstr(writer, Fprofile_UnicodeToUtf8(code->co_name));
#endif

#if PY_VERSION_HEX >= 0x030a00a0
                Py_DECREF(code);
#endif
            }
            mpack_finish_array(writer);
            break;
        case PyTrace_C_CALL: {
            mpack_start_array(writer, 4);
            mpack_write_cstr(writer, "NativeCall");

            mpack_start_array(writer, 2);
            mpack_write_u32(writer, tsc.tv_sec);
            mpack_write_u32(writer, tsc.tv_nsec);
            mpack_finish_array(writer);

            {
                // Attempt to determine what module/class this function belongs
                // to.
                PyObject*   self        = fn->m_self;
                PyObject*   module      = fn->m_module;
                const char* name        = fn->m_ml->ml_name;
                const char* module_name = NULL;

                // Check if we belong to a module, and if not we must be a
                // method.  We do this order to avoid finding that the object
                // we belong to is of type module.
                if (module != NULL) {
                    if (PyModule_Check(module)) {
                        module_name = PyModule_GetName(module);
                    } else if (PyUnicode_Check(module)) {
                        module_name = PyUnicode_AsUTF8(module);
                    }
                } else if (self != NULL) {
                    // This is a method call on a class.
                    module_name = self->ob_type->tp_name;
                }

                mpack_write_cstr(writer, name != NULL ? name : "NULL");
                mpack_write_cstr(writer, module_name != NULL ? module_name : "NULL");
            }
            mpack_finish_array(writer);
            break;
        }
        case PyTrace_C_RETURN:
            mpack_start_array(writer, 3);
            mpack_write_cstr(writer, "NativeReturn");

            mpack_start_array(writer, 2);
            mpack_write_u32(writer, tsc.tv_sec);
            mpack_write_u32(writer, tsc.tv_nsec);
            mpack_finish_array(writer);

            {
                const char* name = fn->m_ml->ml_name;
                mpack_write_cstr(writer, name != NULL ? name : "NULL");
            }
            mpack_finish_array(writer);
            break;
        default:
            // TODO: We should handle exceptions here (or somewhere similar).
            break;
    }

    if (moduleConfiguration.immediateFlushes) {
        mpack_writer_flush_message(writer);
    }

    return 0;
}

// This is installed as the setprofile() handler for new threads by
// threading.setprofile().  On its first execution, it initializes tracing for
// the thread, including creating the thread state, before replace itself with
// the normal Fprofile_FunctionTrace handler.
static PyObject* Fprofile_ThreadFunctionTrace(PyObject* obj, PyFrameObject* frame,
    int what, PyObject* arg) {
    Fprofile_CreateThreadState();

    // Replace our setprofile() handler with the real one.
    PyEval_SetProfile(Fprofile_FunctionTrace, NULL);

    // We previously called `Fprofile_FunctionTrace` to manually recorded this
    // call, but that's both not very interesting as well as causes crashes on
    // startup for some Python versions (due to insufficiently initialized
    // frames), so we don't do that anymore.
    Py_RETURN_NONE;
}

static PyObject* Fprofile_LoggingHook(HookedFunction* hook, PyObject* args, PyObject* kwargs) {
    Writer*  writer = Fprofile_Writer();
    Timestamp   tsc = Fprofile_Time();
    PyObject*   str = PyObject_Str(args);
    const char* log = str != NULL ? PyUnicode_AsUTF8(str) : "<invalid string>";

    if (writer != NULL) {
        mpack_start_array(writer, 4);
        mpack_write_cstr(writer, "Log");

        mpack_start_array(writer, 2);
        mpack_write_u32(writer, tsc.tv_sec);
        mpack_write_u32(writer, tsc.tv_nsec);
        mpack_finish_array(writer);

        char buffer[128] = { 0 };
        snprintf(buffer, sizeof(buffer), "%s.%s", hook->module, hook->fn.ml_name);
        mpack_write_cstr(writer, buffer);

        mpack_write_cstr(writer, log);
        mpack_finish_array(writer);

        if (moduleConfiguration.immediateFlushes) {
            mpack_writer_flush_message(writer);
        }
    }

    // Delegate to the original function now that we've logged its arguments.
    return PyObject_Call(hook->original, args, kwargs);
}

static PyObject* Fprofile_ImportHook(HookedFunction* hook, PyObject* args, PyObject* kwargs) {
    Writer*   writer = Fprofile_Writer();
    Timestamp tsc    = Fprofile_Time();

    if (writer != NULL) {
        const char* import = "<unknown module>";
        PyObject*   ignore = NULL;
        int         level  = 0;

        // Parse the args for __import__ to find the module we're looking for.
        if (!PyArg_ParseTuple(args, "sOOOi", &import, &ignore, &ignore, &ignore, &level)) {
            // We got some weird looking args - let's carry on rather than dying.
            PyErr_Clear();
        }

        mpack_start_array(writer, 3);
        mpack_write_cstr(writer, "Import");

        mpack_start_array(writer, 2);
        mpack_write_u32(writer, tsc.tv_sec);
        mpack_write_u32(writer, tsc.tv_nsec);
        mpack_finish_array(writer);

        mpack_write_cstr(writer, import);
        mpack_finish_array(writer);

        if (moduleConfiguration.immediateFlushes) {
            mpack_writer_flush_message(writer);
        }
    }

    // Delegate to the original function now that we've logged its arguments.
    return PyObject_Call(hook->original, args, kwargs);
}

////////////////////////////////////////////////////////////////////////////////
// Configuration
////////////////////////////////////////////////////////////////////////////////
static PyObject* Fprofile_ConfigEnableMemoryTracing(void) {
    // We can't have already enabled memory tracing.
    assert(!moduleConfiguration.enableMemoryTracing);
    moduleConfiguration.enableMemoryTracing = true;

    if (moduleConfiguration.started) {
        // We've already started, so let's start memory tracing at this point.
        Fprofile_RecordAllocations();
    }

    Py_RETURN_NONE;
}

////////////////////////////////////////////////////////////////////////////////
// Shutdown/Cleanup
////////////////////////////////////////////////////////////////////////////////
// Called when the process is shutting down.  Stop tracing and flush the buffer.
// This is always called on the main thread.
static PyObject* Fprofile_Terminate(void) {
    ThreadState* state = pthread_getspecific(Tss_Key);

    // Stop profiling and don't allow further logging, then flush any remaining
    // messages.
    moduleConfiguration.started = false;
    PyEval_SetProfile(NULL, NULL);
    Fprofile_ThreadTeardown(state);

    Py_RETURN_NONE;
}

// Called when the thread has shut down, including in multithread/process
// situations.  Flush the buffer to ensure we're getting all of the recorded
// data.
static void Fprofile_ThreadTeardown(void* key) {
    ThreadState* state = key;
    if (state == NULL) {
        // We never fully initialized this thread, so skip teardown.
        return;
    }

    mpack_writer_flush_message(&state->writer);
}

static PyObject* Fprofile_MpexitHook(HookedFunction* hook, PyObject* args, PyObject* kwargs) {
    // We're a multithreaded process and we've been notified that we're exiting.
    // Manually run our thread's teardown, as multiprocessing won't call our
    // normal atexit() handler.
    ThreadState* state = pthread_getspecific(Tss_Key);

    Fprofile_ThreadTeardown(state);
    return PyObject_Call(hook->original, args, kwargs);
}

////////////////////////////////////////////////////////////////////////////////
// Module Initialization
////////////////////////////////////////////////////////////////////////////////
static PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_functiontrace",
    "",
    -1,
    methods
};

PyMODINIT_FUNC PyInit__functiontrace(void) {
    if (pthread_key_create(&Tss_Key, Fprofile_ThreadTeardown)) {
        perror("Failed to create Tss_Key");
        exit(-1);
    }


    PyObject* m = PyModule_Create(&module);
    if (PyModule_AddStringConstant(m, "__version__", PACKAGE_VERSION) == -1) {
      Py_XDECREF(m);
      m = NULL;
    }

    return m;
}

// Start tracing.
// Takes the directory to output profile files to as an argument.
static PyObject* Fprofile_StartTrace(PyObject* obj, PyObject* args, PyObject* kwargs) {
    // We'll only explicitly start the trace once.  Take this as an indicator
    // that we're the main thread.

    ////////////////////////////////////////////////////////////////////////////
    // Process Information
    ////////////////////////////////////////////////////////////////////////////
    // Find some information about our process out.  We'll need this to
    // register threads or create a new FunctionTrace session.

    // There doesn't appear to be a straightfoward C API to get sys.argv
    // pyconfig in 3.8 might provide some other options... For now just fetch
    // the python argv object from sys
    PyObject* pythonArgv = PySys_GetObject("argv");
    assert(pythonArgv != NULL);

    if (PyList_Check(pythonArgv)) {
        size_t index = 0;

        // Append each argument we have room for onto our argv string.
        for (int i = 0; (index < sizeof(moduleConfiguration.argv)) &&
                (i < PyList_Size(pythonArgv)); i++) {
            index += snprintf(
                &moduleConfiguration.argv[index],
                sizeof(moduleConfiguration.argv) - index,
                "%s " ,
                PyUnicode_AsUTF8(PyList_GetItem(pythonArgv, i))
            );
        }
    }

    moduleConfiguration.pid = getpid();

    // Mark that we'll need to forget some information on forks.  In
    // particular, we shouldn't think that we have a thread that's sent any
    // information.
    if (pthread_atfork(NULL, NULL, Fprofile_ResetThreadState) != 0) {
        perror("Failed to register pthread_atfork() handler");
        exit(-1);
    }

    ////////////////////////////////////////////////////////////////////////////
    // Initialization Message
    ////////////////////////////////////////////////////////////////////////////
    // Check if we're in a subprocess of a command being run under
    // functiontrace.  If we are, we should connect to the same socket and
    // notify it somehow that we belong to a different process.  Otherwise, we
    // should setup various profiling information.
    const char* breadcrumb      = "FUNCTIONTRACE_LIVE";
    const char* existingProfile = getenv(breadcrumb);
    if (existingProfile == NULL) {
        // We're the top level interpreter.
        Timestamp   time                      = Fprofile_Time();
        char        traceInitialization[1024] = { 0 };
        Writer      initWriter                = { 0 };
        intptr_t    sock                      = -1;
        const char* version                   = Py_GetVersion();
        const char* platform                  = Py_GetPlatform();
        char*       outputDirectory           = NULL;

        // Parse the args to figure out what our output directory is.
        if (!PyArg_ParseTuple(args, "s", &outputDirectory)) {
            printf("%s\n", outputDirectory);
            perror("Invalid functiontrace --output_dir arguments");
            exit(-1);
        }

        // Spawn the server and wait for it to connect.
        pid_t server = fork();
        if (server == 0) {
            // Detach ourselves as a daemon
            if (setsid() == -1) {
                perror("Failed to detach profile server");
                exit(-1);
            }

            char* cmd[] = {
                "functiontrace-server",
                "--directory",
                outputDirectory,
                NULL
            };
            execvp("functiontrace-server", cmd);
            perror("Failed to spawn profile server");
            exit(-1);
        } else if (server == -1) {
            perror("Failed to fork profile server");
            exit(-1);
        }

        moduleConfiguration.socket = (struct sockaddr_un) { .sun_family = AF_UNIX };
        snprintf((char*) &moduleConfiguration.socket.sun_path,
                sizeof(moduleConfiguration.socket.sun_path),
                "/tmp/functiontrace-server.sock.%d", server);

        // Generate the TraceInitialization message to the profiler server telling
        // them about the profile we'll be creating.
        if ((sock = socket(AF_UNIX, SOCK_STREAM, 0)) == -1) {
            perror("TraceInitialization socket failed to spawn");
            exit(-1);
        }

        // Wait for 1s for the functiontrace-server to be ready to receive
        // connections.
        for (size_t tries = 0; true; tries++) {
            if (connect(sock, (struct sockaddr*) &moduleConfiguration.socket,
                        sizeof(moduleConfiguration.socket)) == 0) {
                break;
            }

            if (tries == 1000) {
                // If we haven't connected by now, we never will.
                perror("Failed to connect to TraceInitialization socket");
                exit(-1);
            }

            // We sleep 1ms at a time since we're profiling python and can
            // afford to wait.
            usleep(1000);
        }

        // Register an env var so subprocesses know how to connect to our
        // profile.
        if (setenv(breadcrumb, (char*) &moduleConfiguration.socket.sun_path, 0)) {
            perror("Failed to set recursive breadcrumb");
            exit(-1);
        }

        // Setup a local Mpack context for this first message.
        mpack_writer_init(&initWriter, (char*) &traceInitialization, sizeof(traceInitialization));
        mpack_writer_set_context(&initWriter, (void*) sock);
        mpack_writer_set_flush(&initWriter, &Mpack_Flush);

        mpack_start_map(&initWriter, 5);
        {
            mpack_write_cstr(&initWriter, "program_name");
            mpack_write_cstr(&initWriter, moduleConfiguration.argv);

            // PACKAGE_VERSION is defined in setup.py.
            mpack_write_cstr(&initWriter, "program_version");
            mpack_write_cstr(&initWriter, "py-functiontrace " PACKAGE_VERSION);

            char versionBuf[20] = { 0 };
            snprintf(versionBuf, sizeof(versionBuf), "Python %.*s",
                    (int) (strchr(version, ' ') - version), // Take until the first space in version
                    version);
            mpack_write_cstr(&initWriter, "lang_version");
            mpack_write_cstr(&initWriter, versionBuf);

            mpack_write_cstr(&initWriter, "platform");
            mpack_write_cstr(&initWriter, platform);

            mpack_write_cstr(&initWriter, "time");
            mpack_start_array(&initWriter, 2);
            {
                mpack_write_u32(&initWriter, time.tv_sec);
                mpack_write_u32(&initWriter, time.tv_nsec);
            }
            mpack_finish_array(&initWriter);
        }
        mpack_finish_map(&initWriter);

        // Flush the buffer to ensure the TraceInitialization message is sent
        // out first.
        mpack_writer_flush_message(&initWriter);

        if (shutdown(sock, SHUT_WR) != 0) {
            perror("Failed to close TraceInitialization socket");
            exit(-1);
        }
    } else {
        // Read the socket addr out of `existingProfile` so our threads know
        // how to talk to the profile server.
        moduleConfiguration.socket = (struct sockaddr_un) { .sun_family = AF_UNIX };
        snprintf((char*) &moduleConfiguration.socket.sun_path,
                sizeof(moduleConfiguration.socket.sun_path), "%s", existingProfile);
    }

    ////////////////////////////////////////////////////////////////////////////
    // Tracing Initialization
    ////////////////////////////////////////////////////////////////////////////
    ThreadState* state = Fprofile_CreateThreadState();
    assert(state != NULL);

    // bugs.python.org/issue21512
    // Things can get into a weird state during shutdown due to GC.  Halt
    // our tracing instead to avoid odd behaviour.
    //
    // Python: atexit.register(Fprofile_Terminate)
    {
        PyObject* atexit = PyImport_ImportModule("atexit");
        assert(atexit != NULL);
        PyObject* atexit_register = PyObject_GetAttrString(atexit, "register");
        PyObject* handler = PyCFunction_New(&methods[METHOD_TERMINATE], PyImport_AddModule("_functiontrace"));

        PyObject* callback = Py_BuildValue("(O)", handler);
        PyObject_CallObject(atexit_register, callback);

        Py_DECREF(handler);
    }

    // Register our tracing functions - both the normal one and the
    // multithreaded handler.
    PyEval_SetProfile(Fprofile_FunctionTrace, NULL);

    // Python: threading.setprofile(Fprofile_FunctionTrace)
    {
        PyObject* threading = PyImport_ImportModule("threading");
        assert(threading != NULL);
        PyObject* setprofile = PyObject_GetAttrString(threading, "setprofile");

        PyObject* handler = PyCFunction_New(&methods[METHOD_FUNCTIONTRACE], NULL);
        PyObject* callback = Py_BuildValue("(N)", handler);
        Py_INCREF(callback);

        if (PyObject_CallObject(setprofile, callback) == NULL) {
            perror("Failed to call threading.setprofile() properly");
            exit(-1);
        }
    }

    // We hook functions after doing everything else, just in case we're using
    // a function we want to hook internally.
    Fprofile_HookFunctions();

    if (moduleConfiguration.enableMemoryTracing) {
        // Memory tracing may have up to 40% overhead on traces with many small
        // allocations, so is not enabled by default.
        Fprofile_RecordAllocations();
    }

    // We're now started and allowed to send messages.
    moduleConfiguration.started = true;
    Py_RETURN_NONE;
}

static ThreadState* Fprofile_CreateThreadState(void) {
    ThreadState* state = calloc(1, sizeof(ThreadState));

    // We shouldn't have a ThreadState setup yet, as we're the ones that create
    // it.
    assert(Tss_Key != 0);
    assert(pthread_getspecific(Tss_Key) == NULL);
    assert(state != NULL);

    // Store our state in thread-specific storage so we can find it in the
    // future.
    if (pthread_setspecific(Tss_Key, state)) {
        perror("Failed to set tss_key on thread startup");
        exit(-1);
    }

    // Allocate a socket to report this thread's information back to the
    // profile server.
    if ((state->socket = socket(AF_UNIX, SOCK_STREAM, 0)) == -1) {
        perror("Thread startup socket generation failed");
        exit(-1);
    }

    if (connect(state->socket, (struct sockaddr*)&moduleConfiguration.socket,
                sizeof(moduleConfiguration.socket)) == -1) {
        perror("Thread startup connection error");
        exit(-1);
    }

    // Register a messagepack writer for this thread, including telling it to
    // flush on this thread's socket once the buffer fills up.
    mpack_writer_init(&state->writer, (char*) &state->buffer, sizeof(state->buffer));
    mpack_writer_set_context(&state->writer, (void*) state->socket);
    mpack_writer_set_flush(&state->writer, &Mpack_Flush);

    // Send a message about our thread's registration.
    Timestamp time = Fprofile_Time();
    mpack_start_array(&state->writer, 4);
    {
        mpack_write_cstr(&state->writer, "RegisterThread");

        mpack_start_array(&state->writer, 2);
        {
            mpack_write_u32(&state->writer, time.tv_sec);
            mpack_write_u32(&state->writer, time.tv_nsec);
        }
        mpack_finish_array(&state->writer);

        mpack_write_cstr(&state->writer, moduleConfiguration.argv);
        mpack_write_u32(&state->writer, moduleConfiguration.pid);
    }
    mpack_finish_map(&state->writer);

    // Flush the state of our new thread to ensure that we'll record
    // *something* for it in the case where we quickly exit after opening the
    // socket.
    //
    // TODO: We should have a different approach that doesn't require explicit
    // flushing.  The obvious candidate is shared-mem, but that opens us up to
    // a whole pile of issues we'd hoped to avoid.
    mpack_writer_flush_message(&state->writer);

    return state;
}

// We have some existing thread state that we should free and forget about
// before resuming logging.
// This is useful when we've just forked and want to ensure we don't reuse an
// existing socket.
static void Fprofile_ResetThreadState(void) {
    if (!moduleConfiguration.started) {
        // We haven't actually started yet, but are for some reason being asked
        // to fork.  This appears to be OS dependent.
        return;
    }

    ThreadState* state = pthread_getspecific(Tss_Key);
    assert(state != NULL);

    pthread_setspecific(Tss_Key, NULL);
    close(state->socket);
    free(state);

    // Create a new thread for this process.  We don't need to start an entire
    // new trace like with subprocess calls since we were forked and therefore
    // already share our moduleConfiguration.  However, we do need to record
    // the new pid since we're in a new process.
    moduleConfiguration.pid = getpid();
    Fprofile_CreateThreadState();
}

