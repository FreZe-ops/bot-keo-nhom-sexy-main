import paramiko
import sys

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)

script = r'''
const { chromium } = require('playwright');
// We will test finding all buttons and text on the page
'''

print("Connected to VPS")
ssh.close()
