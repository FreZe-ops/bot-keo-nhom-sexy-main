import urllib.request
import json
import time

API_BASE_URL = 'http://180.93.235.84:3201'

def check():
    for ns in ['NS1', 'NS2', 'NS3', 'NS4']:
        try:
            url = f"{API_BASE_URL}/api/get-active-table?nameService={ns}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as r:
                data = json.loads(r.read().decode('utf-8'))
                table = data.get('activeTable')
                paused = data.get('paused')
                
                shot_url = f"{API_BASE_URL}/api/latest-screenshot?tableName={table}" if table and table not in ('NONE', 'LOBBY') else None
                age = "N/A"
                if shot_url:
                    try:
                        with urllib.request.urlopen(urllib.request.Request(shot_url), timeout=3) as sr:
                            sdata = json.loads(sr.read().decode('utf-8'))
                            if sdata.get('success') and sdata.get('data'):
                                stamp = sdata['data'].get('stampTime', 0)
                                age = f"{time.time() - stamp/1000:.1f}s"
                    except Exception:
                        pass
                print(f"{ns}: table={table} | paused={paused} | image_age={age}")
        except Exception as e:
            print(f"{ns}: error {e}")

check()
