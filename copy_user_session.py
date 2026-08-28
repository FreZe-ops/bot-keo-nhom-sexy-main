import shutil

src = r'C:\Users\administrator\tele_session_84365618453.session'
dst = r'C:\apps\bot-keo-nhom-bcr-main\user_session_84365618453.session'
shutil.copyfile(src, dst)
print('COPIED SUCCESSFULLY!')
