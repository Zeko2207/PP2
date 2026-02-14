#The else keyword catches anything which isn't caught by the preceding conditions.
#The else statement is executed when the if condition evaluate to False.
a = 200
b = 33
if b > a:
  print("b is greater than a")
else:
  print("b is not greater than a")

#The else statement provides a default action when none of the previous conditions are true. 
#Think of it as a "catch-all" for any scenario not covered by your if statement.

#Checking even or odd numbers:
number = 7

if number % 2 == 0:
  print("The number is even")
else:
  print("The number is odd")

#The else statement acts as a fallback that executes when none of the preceding conditions are true.
#This makes it useful for error handling, validation, and providing default values.
username = "Emil"

if len(username) > 0:
  print(f"Welcome, {username}!")
else:
  print("Error: Username cannot be empty")