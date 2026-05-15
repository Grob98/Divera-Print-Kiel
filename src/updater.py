import os
import shutil
import subprocess
import time

OLD_EXE = "myapp.exe"
NEW_EXE = "update/myapp.exe"

time.sleep(2)

shutil.copy2(NEW_EXE, OLD_EXE)

subprocess.Popen([OLD_EXE])