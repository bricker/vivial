import eave.stdlib.pytracing

class Person:
    name: str
    age: int

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    def __repr__(self) -> str:
        return f"{self.name} ({self.age})"


def print_person_name():
    p = Person("Bryan", 35)
    print(p.name)

def print_person_age():
    p = Person("Bryan", 35)
    print(p.age)

def print_person_repr():
    p = Person("Bryan", 35)
    print(p)

if __name__ == "__main__":
    eave.stdlib.pytracing.start_tracing()

    print_person_name()
    print_person_age()
    print_person_repr()
