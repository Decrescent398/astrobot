import os
import paramiko
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
from scp import SCPClient
from src.posts import *

load_dotenv()
npass = os.getenv('NEST-PASS')

ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('hackclub.app', username='decrescent', password=npass)

with SCPClient(ssh.get_transport()) as scp:
    scp.get('/home/decrescent/Astrobot/data/out/meta', 'C:/Users/hridd/Desktop/Docs/Codespace/Astrobot/data/out/', recursive=True)
    scp.get('/home/decrescent/Astrobot/data/out/articles', 'C:/Users/hridd/Desktop/Docs/Codespace/Astrobot/data/out/', recursive=True)
    
ssh.close()

def run_pending():
    window.destroy()
    # post_medium()
    post_news()

window = tk.Tk()
window.title('Astrobot')

label = tk.Label(
    text=f"Run {len(os.listdir('C:/Users/hridd/Desktop/Docs/Codespace/Astrobot/data/out/meta'))} pending astrobot tasks",
    width=50
)
label.pack()

run_button = tk.Button(
    text="Run",
    width="5",
    command=run_pending,
    highlightthickness=2,
    highlightcolor="black"
)
run_button.pack()

window.mainloop()