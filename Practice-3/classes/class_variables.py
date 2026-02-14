#A class variable is a variable that belongs to the class itself rather than to any specific object. All instances of the class share the same copy of this variable.
class Student:
    school = "ABC School"   # Class variable

s1 = Student()
s2 = Student()

print(s1.school)
print(s2.school)

#Instance variables are variables that belong to a specific object.
#Each object maintains its own copy of these variables.
class Student:
    def __init__(self, name):
        self.name = name   # Instance variable

s1 = Student("Jake")
s2 = Student("Emily")

print(s1.name)
print(s2.name)

#This example demonstrates how class variables are shared and instance variables remain separate.
class CSStudent:
    stream = 'cse'          # Class variable

    def __init__(self, name, roll):
        self.name = name    # Instance variable
        self.roll = roll    # Instance variable

# Creating objects
a = CSStudent('Rose', 1)
b = CSStudent('Nat', 2)

print(a.stream)
print(b.stream)
print(a.name)
print(b.name)

#Class variables can be modified in two ways.
#However, only one method is recommended because it avoids confusion.
CSStudent.stream = 'mech'
print(a.stream)
print(b.stream)

