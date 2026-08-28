import os
import subprocess

print("=== PROCESSES ===")
try:
  print(
      subprocess.check_output("tasklist", shell=True)
      .decode("ascii", errors="ignore")[:3000]
  )
except Exception as e:
  print("Tasklist err:", e)

print("\n=== LOGS (LAST 10 LINES EACH) ===")
log_dir = r"C:\apps\bot-keo-nhom-bcr-main\logs"
if os.path.exists(log_dir):
  for f in os.listdir(log_dir):
    fp = os.path.join(log_dir, f)
    if os.path.isfile(fp):
      print(f"\n--- {f} ---")
      try:
        with open(fp, "r", encoding="utf-8", errors="replace") as fh:
          lines = fh.readlines()
          for l in lines[-10:]:
            print(l.strip().encode("ascii", errors="replace").decode("ascii"))
      except Exception as ex:
        print("err:", ex)
