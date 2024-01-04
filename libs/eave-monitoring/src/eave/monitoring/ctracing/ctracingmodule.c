#define PY_SSIZE_T_CLEAN
#include <Python.h>

// https://devdocs.io/python~3.11/c-api/init#c.PyEval_SetTrace
static int
tracefunc(PyObject *obj, PyFrameObject *frame, int what, PyObject *arg)
{
    return 0;
}

static PyObject *
start_tracing(PyObject *self, PyObject *args)
{
    PyEval_SetTrace(tracefunc, NULL);

    // Note that void return types aren't supported for these functions, a segmentation fault occurs.
    return Py_NewRef(Py_None);
}

static PyObject *
start_profiling(PyObject *self, PyObject *args)
{
    PyEval_SetProfile(tracefunc, NULL);

    // Note that void return types aren't supported for these functions, a segmentation fault occurs.
    return Py_NewRef(Py_None);
}

// static void
// stop()
// {
//     PyEval_SetTrace(NULL, NULL);
// }

static PyMethodDef ctracing_methods[] = {
    {"start_tracing", start_tracing, METH_VARARGS, "Starts the Eave tracing agent."},
    {"start_profiling", start_profiling, METH_VARARGS, "Starts the Eave profiling agent."},
    // {"stop", stop, METH_NOARGS, "Stops the Eave tracing agent."},
    {NULL, NULL}
};


static struct PyModuleDef ctracingmodule = {
    PyModuleDef_HEAD_INIT,
    "ctracing",
    "Manage the Eave tracing agent.",
    0,
    ctracing_methods
};


PyMODINIT_FUNC PyInit_ctracing(void) {
    return PyModule_Create(&ctracingmodule);
}