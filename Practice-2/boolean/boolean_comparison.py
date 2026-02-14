#When you run a condition in an if statement, Python returns True or False:
a = 200
b = 33

#Print a message based on whether the condition is True or False
if b > a:
  print("b is greater than a")
else:
  print("b is not greater than a")

#The bool() function allows you to evaluate any value, and give you True or False in return
print(bool("Hello")) # returns True
print(bool(15)) # returns True

#Almost any value is evaluated to True if it has some sort of content
#Any string is True, except empty strings.
#Any number is True, except 0.
#Any list, tuple, set, and dictionary are True, except empty ones.

#The following will return False:
bool(False)
bool(None)
bool(0)
bool("")
bool(())
bool([])
bool({})

#You can create functions that returns a Boolean Value:
def myFunction() :
  return True

print(myFunction())