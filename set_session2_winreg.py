import winreg

key_path = r"SYSTEM\CurrentControlSet\Services\BCR-session2\Parameters"
key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_ALL_ACCESS)

env_values = [
    "PLAYWRIGHT_BROWSERS_PATH=C:\\ms-playwright",
    "ACCOUNT_INDEX=2",
    "PREFERRED_TABLE=C02",
    "DOTENV_CONFIG_PATH=C:\\apps\\bot-keo-nhom-bcr-main\\.env"
]

winreg.SetValueEx(key, "AppEnvironmentExtra", 0, winreg.REG_MULTI_SZ, env_values)
winreg.CloseKey(key)

print("Successfully written REG_MULTI_SZ to BCR-session2 Parameters!")
