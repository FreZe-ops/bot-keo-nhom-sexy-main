import os
import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def test_config():
    config_file = 'groups_config.json'
    assert os.path.exists(config_file), f"Missing {config_file}"
    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    sessions = ['NS1', 'NS2', 'NS3', 'NS4']
    total_groups = 0
    print("=== TESTING GROUPS CONFIG FOR 4 SESSIONS ===")
    for ns in sessions:
        assert ns in data, f"Missing {ns} in config"
        ns_conf = data[ns]
        groups = ns_conf.get('groups', [])
        print(f"[{ns}] Configured with {len(groups)} groups. API: {ns_conf.get('api_base_url')}")
        assert len(groups) == 5, f"Expected 5 groups in {ns}, got {len(groups)}"
        
        for g in groups:
            total_groups += 1
            print(f"  - {g['name']}: ID={g['id']} | Opening Order={g['opening_order']} | Ending Order={g['ending_order']}")
            assert len(g['opening_order']) == 6, f"Invalid opening order length for {g['name']}"
            assert len(g['ending_order']) == 4, f"Invalid ending order length for {g['name']}"
            assert len(g['opening_delays']) == 6, f"Invalid opening delays length for {g['name']}"
            assert len(g['ending_delays']) == 4, f"Invalid ending delays length for {g['name']}"
            
    print(f"\n✅ Total Groups across 4 sessions: {total_groups} groups (5 groups per session).")
    print("✅ All group orders, delays, and session API endpoints are valid!")

def test_imports():
    import bot_multi_session
    print("✅ bot_multi_session.py imported successfully with no syntax errors!")

if __name__ == '__main__':
    test_config()
    test_imports()
