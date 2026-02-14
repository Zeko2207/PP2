#Information can be passed into functions as arguments.
#Arguments are specified after the function name, inside the parentheses.
#You can add as many arguments as you want, just separate them with a comma.
#The following example has a function with one argument (fname). When the function is called,
#we pass along a first name, which is used inside the function to print the full name:
def my_function(fname):
  print(fname + " Refsnes")

my_function("Emil")
my_function("Tobias")
my_function("Linus")

def my_function(name): # name is a parameter
  print("Hello", name)

my_function("Emil") # "Emil" is an argument

#By default, a function must be called with the correct number of arguments.
#If your function expects 2 arguments, you must call it with exactly 2 arguments.
#This function expects 2 arguments, and gets 2 arguments:
def my_function(fname, lname):
  print(fname + " " + lname)

my_function("Emil", "Refsnes")

#If you try to call the function with the wrong number of arguments,
#you will get an error

#You can assign default values to parameters. 
#If the function is called without an argument, it uses the default value:
def my_function(name = "friend"):
  print("Hello", name)

my_function("Emil")
my_function("Tobias")
my_function()
my_function("Linus")

#You can send arguments with the key = value syntax.
def my_function(animal, name):
  print("I have a", animal)
  print("My", animal + "'s name is", name)

my_function(animal = "dog", name = "Buddy")
#This way, with keyword arguments, the order of the arguments does not matter

#When you call a function with arguments without using keywords,
#they are called positional arguments.
#Positional arguments must be in the correct order:
def my_function(animal, name):
  print("I have a", animal)
  print("My", animal + "'s name is", name)

my_function("dog", "Buddy")
#Switching the order changes the result:
def my_function(animal, name):
  print("I have a", animal)
  print("My", animal + "'s name is", name)

my_function("Buddy", "dog")

