class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname

  def printname(self):
    print(self.firstname, self.lastname)

#So far we have created a child class that inherits the properties and methods from its parent.
#We want to add the __init__() function to the child class (instead of the pass keyword).

#The __init__() function is called automatically every time the class is being used to create a new object.

#Add the __init__() function to the Student class:
class Student(Person):
  def __init__(self, fname, lname):
     pass
    #add properties etc.

#When you add the __init__() function, the child class will no longer inherit the parent's __init__() function.
#The child's __init__() function overrides the inheritance of the parent's __init__() function.

#To keep the inheritance of the parent's __init__() function, add a call to the parent's __init__() function:
class Student(Person):
    def __init__(self, fname, lname):
        Person.__init__(self, fname, lname)