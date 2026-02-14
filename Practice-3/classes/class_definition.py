#Python is an object oriented programming language.
#Almost everything in Python is an object, with its properties and methods.
#A Class is like an object constructor, or a "blueprint" for creating objects.

#To create a class, use the keyword class:
class MyClass:
  x = 5

#Now we can use the class named MyClass to create objects:
p1 = MyClass()
print(p1.x)

#You can delete objects by using the del keyword:
del p1

#You can create multiple objects from the same class:
p1 = MyClass()
p2 = MyClass()
p3 = MyClass()

print(p1.x)
print(p2.x)
print(p3.x)

#class definitions cannot be empty, 
#but if you for some reason have a class definition with no content,
#put in the pass statement to avoid getting an error.
class Person:
  pass