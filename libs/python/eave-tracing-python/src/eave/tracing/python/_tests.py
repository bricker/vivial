import _functiontrace

def func1():
    print("func1")

def func2():
    print("func2")

def func3():
    print("func3")

if __name__ == "__main__":
    _functiontrace.begin_tracing(".")

    func1()
    func2()
    func3()