#Python supports the usual logical conditions from mathematics
#These conditions can be used in several ways, most commonly in "if statements" and loops.
#An "if statement" is written by using the if keyword.
a = 33
b = 200
if b > a: #True
  print("b is greater than a") #returns "b is greater than a"

#The if statement evaluates a condition (an expression that results in True or False).
#If the condition is true, the code block inside the if statement is executed.
# If the condition is false, the code block is skipped.

#You can have multiple statements inside an if block. All statements must be indented at the same level.
age = 20
if age >= 18:
  print("You are an adult")
  print("You can vote")
  print("You have full legal rights")

#Boolean variables can be used directly in if statements without comparison operators.
is_logged_in = True
if is_logged_in:
  print("Welcome back!")

