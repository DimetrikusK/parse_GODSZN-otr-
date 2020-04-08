import os
f = open('C:/Users/user/Desktop/text.txt', 'r')
list = f.read().strip()
file = list.split()

os.makedirs(file[2], mode=0o777, exist_ok=False)
os.makedirs(file[3], mode=0o777, exist_ok=False)
os.makedirs(file[4], mode=0o777, exist_ok=False)
os.makedirs(file[5], mode=0o777, exist_ok=False)
os.makedirs(file[6], mode=0o777, exist_ok=False)