import os

p = r'C:\apps\bot-keo-nhom-bcr-main'
files = [f for f in os.listdir(p) if f.endswith('.session')]
print('Session files in C:\\apps\\bot-keo-nhom-bcr-main:', files)
