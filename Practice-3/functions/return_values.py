#Functions can send data back to the code that called them using the return statement.
#When a function reaches a return statement, it stops executing and sends the result back:
def get_greeting():
  return "Hello from a function"

message = get_greeting()
print(message)

#You can use the returned value directly:
def get_greeting():
  return "Hello from a function"

print(get_greeting())


def my_function(x, y):
  return x + y

result = my_function(5, 3)
print(result)

