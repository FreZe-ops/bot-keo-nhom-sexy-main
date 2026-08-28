import os

for root, dirs, files in os.walk(r'C:\Users\administrator'):
  for f in files:
    if '84365618453' in f:
      print(os.path.join(root, f))

for root, dirs, files in os.walk(r'C:\apps'):
  for f in files:
    if '84365618453' in f:
      print(os.path.join(root, f))
