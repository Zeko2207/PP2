import re

receipt_text = open("raw.txt", encoding="utf-8").read()

x = re.findall(r'(?<!\d)(?:\d{1,3}(?: \d{3})*),\d{2}(?!\d)', receipt_text)
print(x)



#18.04.2019 11:13:58
y = re.findall(r'\b\d{2}.\d{2}.\d{4} \d{2}:\d{2}:\d{2}\b', receipt_text)
print(y)