#When a class inherits from more than one base class, it is called multiple inheritance.
#The derived class inherits all features of its base classes.
#Syntax:
class Base1:
     # Body of the class
        pass

class Base2:
    # Body of the class
        pass

class Derived(Base1, Base2):
         # Body of the class
         pass 

#When the method is overridden in both classes
#The code demonstrates multiple inheritance where Class4 inherits from Class2 and Class3;
#calling obj.m() executes Class2’s method because, according to Python’s MRO, Class2 is checked before Class3.
class Class1:
    def m(self):
        print("In Class1") 
      
class Class2(Class1):
    def m(self):
        print("In Class2")

class Class3(Class1):
    def m(self):
        print("In Class3")  
       
class Class4(Class2, Class3):
    pass   
    
obj = Class4()
obj.m()

#When the Method overridden in one class only
#The code shows multiple inheritance where Class4 inherits from Class2 and Class3;
#calling obj.m() executes Class3’s method due to Python’s method resolution order (MRO).
class Class1:
    def m(self):
        print("In Class1")

class Class2(Class1):
    pass

class Class3(Class1):
    def m(self):
        print("In Class3")

class Class4(Class2, Class3):
    pass

obj = Class4()
obj.m()

#All classes define the same method
#The code demonstrates multiple inheritance,
#showing that Class4 overrides the m method,
#but methods from parent classes (Class2, Class3, Class1) can still be called explicitly using the class name.
class Class1:
    def m(self):
        print("In Class1")

class Class2(Class1):
    def m(self):
        print("In Class2")

class Class3(Class1):
    def m(self):
        print("In Class3")

class Class4(Class2, Class3):
    def m(self):
        print("In Class4")

obj = Class4()
obj.m()
Class2.m(obj)
Class3.m(obj)
Class1.m(obj)

#Calling methods of parent classes from child class
#The code demonstrates multiple inheritance and explicitly calls parent class methods,
#showing how Class1.m() is invoked multiple times through Class2 and Class3.
class Class1:
    def m(self):
        print("In Class1")

class Class2(Class1):
    def m(self):
        print("In Class2")
        Class1.m(self)

class Class3(Class1):
    def m(self):
        print("In Class3")
        Class1.m(self)

class Class4(Class2, Class3):
    def m(self):
        print("In Class4")
        Class2.m(self)
        Class3.m(self)

obj = Class4()
obj.m()