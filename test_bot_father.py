import urllib.request
import json
import urllib.parse

TOKEN = "8989118521:AAHHhe-xofyGEppkUUXsjMAiRzroMj5Hbf4"
groups = [
    "-1004308450541",
    "-1004317090903",
    "-1004296530499",
    "-1004426087287",
    "-1002691928353",
    "-1003808252051",
    "-1003931075414"
]

print("=== CHECKING TELEGRAM BOT TOKEN ===")
url = f"https://api.telegram.org/bot{TOKEN}/getMe"
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        res = json.loads(r.read().decode('utf-8'))
        print("getMe Result:", res)
except Exception as e:
    print("getMe Error:", e)

print("\n=== CHECKING ACCESS TO GROUPS ===")
for g in groups:
    test_url = f"https://api.telegram.org/bot{TOKEN}/getChat?chat_id={g}"
    try:
        with urllib.request.urlopen(test_url, timeout=10) as r:
            res = json.loads(r.read().decode('utf-8'))
            print(f"Group {g}: OK -> Title: '{res.get('result', {}).get('title')}'")
    except urllib.error.HTTPError as he:
        err_msg = he.read().decode('utf-8')
        print(f"Group {g}: HTTP {he.code} -> {err_msg}")
    except Exception as e:
        print(f"Group {g}: Error -> {e}")
