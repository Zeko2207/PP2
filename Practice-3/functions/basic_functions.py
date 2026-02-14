#A function is a block of code which only runs when it is called.
#A function can return data as a result.
#A function helps avoiding code repetition.

#In Python, a function is defined using the def keyword,
#followed by a function name and parentheses:
def my_function():
  print("Hello from a function")

#This creates a function named my_function 
#that prints "Hello from a function" when called.

#To call a function, write its name followed by parentheses:
def my_function():
  print("Hello from a function")

my_function()

#You can call the same function multiple times:
def my_function():
  print("Hello from a function")

my_function()
my_function()
my_function()

#Imagine you need to convert temperatures from Fahrenheit to Celsius several times in your program.
#Without functions, you would have to write the same calculation code repeatedly:
#Without functions - repetitive code:
temp1 = 77
celsius1 = (temp1 - 32) * 5 / 9
print(celsius1)

temp2 = 95
celsius2 = (temp2 - 32) * 5 / 9
print(celsius2)

temp3 = 50
celsius3 = (temp3 - 32) * 5 / 9
print(celsius3)

#With functions - reusable code:
def fahrenheit_to_celsius(fahrenheit):
  return (fahrenheit - 32) * 5 / 9

print(fahrenheit_to_celsius(77))
print(fahrenheit_to_celsius(95))
print(fahrenheit_to_celsius(50))

#Function definitions cannot be empty.
#If you need to create a function placeholder without any code,
#use the pass statement:
def my_function():
  pass