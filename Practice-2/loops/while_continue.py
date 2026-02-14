#With the continue statement we can stop the current iteration, and continue with the next:
#Continue to the next iteration if i is 3:
i = 0
while i < 6:
  i += 1
  if i == 3:
    continue
  print(i)

#output: Note that number 3 is missing in the result
#1
#2
#4
#5
#6