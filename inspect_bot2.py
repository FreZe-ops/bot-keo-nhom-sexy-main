import subprocess

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'
for param in ['Application', 'AppParameters', 'AppDirectory', 'AppStdout', 'AppStderr']:
    cmd = f'"{NSSM}" get BCR-bot2 {param}'
    res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    print(f"{param}: {res.stdout.strip()}")

# Start BCR-bot2
res_start = subprocess.run(f'"{NSSM}" start BCR-bot2', capture_output=True, text=True, shell=True)
print(f"Start BCR-bot2: {res_start.stdout.strip()}")
