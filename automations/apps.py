import subprocess

def open_chrome():
    subprocess.run("start chrome", shell=True)

def open_vscode():
    subprocess.run("code", shell=True)
