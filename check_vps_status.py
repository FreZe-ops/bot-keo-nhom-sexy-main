import urllib.request
import json
import time

for ns in ['NS1', 'NS2', 'NS3', 'NS4', 'NS5']:
    url = f'http://127.0.0.1:3201/api/get-active-table?nameService={ns}'
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            d = json.loads(r.read().decode('utf-8'))
            tbl = d.get('activeTable')
            shot_url = f'http://127.0.0.1:3201/api/latest-screenshot?tableName={tbl}'
            sdata = {}
            try:
                with urllib.request.urlopen(shot_url, timeout=3) as sr:
                    sdata = json.loads(sr.read().decode('utf-8'))
            except Exception as se:
                sdata = {'error': str(se)}
            
            stamp = sdata.get('data', {}).get('stampTime')
            age_s = (time.time() * 1000 - stamp) / 1000.0 if stamp else None
            print(f"[{ns}] activeTable={tbl} | shot_age={age_s:.1f}s" if age_s else f"[{ns}] activeTable={tbl} | NO SHOT ({sdata})")
    except Exception as e:
        print(f"[{ns}] error: {e}")
