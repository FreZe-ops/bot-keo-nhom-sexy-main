import glob
import os

all_files = glob.glob('C:/apps/bot-keo-nhom-bcr-main/logs/*')
print("Files in logs:", all_files)
for f in all_files:
    if os.path.isfile(f):
        print(f"=== {os.path.basename(f)} ===")
        try:
            with open(f, 'r', encoding='utf-8', errors='replace') as fp:
                lines = fp.readlines()
                for l in lines[-10:]:
                    print(l.strip())
        except Exception as e:
            print("Error reading:", e)
        print()
