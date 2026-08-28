import urllib.request
import urllib.parse
import json
import time

API_BASE_URL = 'http://localhost:3201'
API_KEY = 'your-static-api-key'

headers = {
    'User-Agent': 'Mozilla/5.0',
    'x-api-key': API_KEY
}

def check_sessions():
    print('=== CHECKING ACTIVE SESSIONS HEALTH ===')
    healthy = []
    for ns in ['NS1', 'NS2', 'NS3', 'NS4']:
        try:
            url = f"{API_BASE_URL}/api/get-active-table?nameService={ns}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=3) as r:
                data = json.loads(r.read().decode('utf-8'))
                paused = data.get('paused', False)
                table = str(data.get('activeTable') or '').upper().strip()
                ready_at = data.get('readyAt')
                print(f"Service {ns}: activeTable='{table}', paused={paused}, readyAt={ready_at}")
                if table and table not in ('NONE', 'LOBBY') and not paused:
                    shot_url = f"{API_BASE_URL}/api/latest-screenshot?tableName={urllib.parse.quote(table)}"
                    shot_req = urllib.request.Request(shot_url, headers=headers)
                    with urllib.request.urlopen(shot_req, timeout=3) as sr:
                        sdata = json.loads(sr.read().decode('utf-8'))
                        if sdata.get('success') and sdata.get('data'):
                            sinfo = sdata['data']
                            stamp = int(sinfo.get('stampTime') or 0)
                            age_s = ((time.time() * 1000) - stamp) / 1000.0 if stamp else 9999
                            print(f"  -> Table {table} screenshot age: {age_s:.1f}s, file={sinfo.get('filepath')}")
                            if age_s < 180:
                                healthy.append({'name_service': ns, 'table': table, 'age_s': age_s})
                        else:
                            print(f"  -> Table {table} no screenshot data")
        except Exception as e:
            print(f"Service {ns} Error: {e}")
    print('\nHEALTHY ACTIVE SESSIONS:', healthy)

if __name__ == '__main__':
    check_sessions()
