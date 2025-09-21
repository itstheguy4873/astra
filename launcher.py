import customtkinter as tk
import tkinter as ntk
import winreg as reg
import pythoncom
import psutil
import logging
import json
import zipfile
import urllib3
import io
import os
from util_toolbox import themes, parse, configpath, cleanup, getasset, Font, centerwindow, extractRoots
from subprocess import Popen
from sys import executable
from PIL import Image
from customtkinter import set_appearance_mode
from pathlib import Path
from win32com.shell import shell # type: ignore
from tkinter import messagebox as mb
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.getLogger('requests').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

def launch(mode='app'):
    try:
        config = parse(configpath)
        theme = config.get('Theme', 'Light')
        font = config.get('Font', 'Inter')
        
        globalfont = Font.new(font, 15)

        main = tk.CTk()
        centerwindow(main, 400, 225)
        main.title('Astra')
        main.resizable(False, False)
        main.iconbitmap(getasset('logo', 'icon', theme))

        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == 'RobloxPlayerBeta.exe'.lower() or proc.info['name'] and proc.info['name'].lower() == 'RobloxStudioBeta.exe'.lower():
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                raise Exception('Roblox could not be closed; close it manually before relaunching')

        rbxpath = Path(os.environ.get('LOCALAPPDATA')) / 'Roblox'

        installdir = rbxpath / 'Astra'

        verUrl = 'https://clientsettingscdn.roblox.com/v2/client-version/WindowsPlayer'
        http = urllib3.PoolManager()
        response = http.request('GET', verUrl)

        if response.status != 200:
            raise Exception('Could not fetch latest Roblox version')
        
        data = json.loads(response.data.decode('utf-8'))
        clientVersion = data.get('clientVersionUpload')
        
        response.release_conn()

        currentver = (installdir / 'version.txt').read_text().strip() if (installdir / 'version.txt').exists() else None
        print(currentver)
        def dlZip(path, root, installdir, http):
            zipUrl = f'https://setup.rbxcdn.com/{clientVersion}-{root}'
            outputDir = installdir / path
            outputDir.mkdir(parents=True, exist_ok=True)

            response = http.request("GET", zipUrl, preload_content=False)
            buf = io.BytesIO()

            while True:
                chunk = response.read(4 * 1024 * 1024)
                if not chunk:
                    break
                buf.write(chunk)
            response.release_conn()

            buf.seek(0)
            try:
                with zipfile.ZipFile(buf, 'r') as zRef:
                    zRef.extractall(outputDir)
                return True
            except zipfile.BadZipFile as e:
                logging.error(f'Failed to extract {root}: {e}')
                return False

        if currentver != clientVersion:
            http = urllib3.PoolManager()

            workers = min(32, (os.cpu_count() or 4) * 5)
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(dlZip, path, root, installdir, http): root
                        for root, path in extractRoots.items()}

                for future in as_completed(futures):
                    root = futures[future]
                    try:
                        if not future.result():
                            logging.error(f"Failed to download {root}")
                    except Exception as e:
                        logging.error(f"Error downloading {root}: {e}")

            http.clear()

            xmlPath = installdir / 'AppSettings.xml'
            if not xmlPath.exists():
                with xmlPath.open('w') as f:
                    f.write('''<?xml version="1.0" encoding="UTF-8"?>
    <Settings>
        <ContentFolder>content</ContentFolder>
        <BaseUrl>http://www.roblox.com</BaseUrl>
    </Settings>
    ''')

            verPath = installdir / 'version.txt'
            if not verPath.exists():
                with verPath.open('w') as f:
                    f.write(clientVersion)    

        falsebg = ntk.Frame(master=main, background=themes[theme]['bg_color'])
        falsebg.pack(expand=True, fill='both')

        logoimage = Image.open(getasset('logo', 'image', theme))
        logoimagetk = tk.CTkImage(logoimage, size=(100, 100) if theme == 'Dark' else (85, 85))
        logolabel = tk.CTkLabel(main, text='', image=logoimagetk, bg_color=themes[theme]['bg_color'])
        logolabel.place(x=155,y=20)

        statustext = tk.CTkLabel(main, text='Updating Roblox', font=globalfont, bg_color=themes[theme]['bg_color'], width=100)
        statustext.place(x=200,y=135, anchor='center')

        statuslabel = tk.CTkProgressBar(main, mode='indeterminate')
        statuslabel.place(x=100,y=175)
        statuslabel.start()

        set_appearance_mode(theme)
        main.configure(bg_color=themes[theme]['bg_color'])

        pythoncom.CoInitialize()
        shelllink = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)

        shelllink.SetPath(str(installdir / 'RobloxPlayerBeta.exe'))
        shelllink.SetArguments('roblox-player:1+launchmode:app')
        shelllink.SetWorkingDirectory(os.path.dirname(str(installdir / 'RobloxPlayerBeta.exe')))
        shelllink.SetIconLocation(str(installdir / 'RobloxPlayerBeta.exe'), 0)

        persistfile = shelllink.QueryInterface(pythoncom.IID_IPersistFile)
        lnk = str(Path(os.environ.get('APPDATA')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Roblox' / 'Roblox Player.lnk')
        persistfile.Save(lnk, 0)

        if mode == 'app':
            proc = Popen([str(installdir / 'RobloxPlayerBeta.exe'), 'roblox-player:1+launchmode:app'])
        if mode.startswith('roblox'):
            proc = Popen([str(installdir / 'RobloxPlayerBeta.exe'), mode])

        main.withdraw()
        main.mainloop()

        cleanup()
    
    except Exception as e:
        mb.showerror('Astra', f'Astra encountered an error: {e}')

def silent_update():
    verUrl = 'https://clientsettingscdn.roblox.com/v2/client-version/WindowsPlayer'
    http = urllib3.PoolManager()
    response = http.request('GET', verUrl)

    if response.status != 200:
        raise Exception('Could not fetch latest Roblox version')
        
    data = json.loads(response.data.decode('utf-8'))
    clientVersion = data.get('clientVersionUpload')
        
    response.release_conn()
    
    rbxpath = Path(os.environ.get('LOCALAPPDATA')) / 'Roblox'

    installdir = rbxpath / 'Astra'

    currentver = (installdir / 'version.txt').read_text().strip() if (installdir / 'version.txt').exists() else None

    def dlZip(path, root, installdir, http):
        zipUrl = f'https://setup.rbxcdn.com/{clientVersion}-{root}'
        outputDir = installdir / path
        outputDir.mkdir(parents=True, exist_ok=True)

        response = http.request("GET", zipUrl, preload_content=False)
        buf = io.BytesIO()

        while True:
            chunk = response.read(4 * 1024 * 1024)
            if not chunk:
                break
            buf.write(chunk)
        response.release_conn()

        buf.seek(0)
        try:
            with zipfile.ZipFile(buf, 'r') as zRef:
                zRef.extractall(outputDir)
            return True
        except zipfile.BadZipFile as e:
            logging.error(f'Failed to extract {root}: {e}')
            return False

    if currentver != clientVersion:
        http = urllib3.PoolManager()

        workers = min(32, (os.cpu_count() or 4) * 5)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(dlZip, path, root, installdir, http): root
                    for root, path in extractRoots.items()}

            for future in as_completed(futures):
                root = futures[future]
                try:
                    if not future.result():
                        logging.error(f"Failed to download {root}")
                except Exception as e:
                    logging.error(f"Error downloading {root}: {e}")

        http.clear()

        xmlPath = installdir / 'AppSettings.xml'
        if not xmlPath.exists():
            with xmlPath.open('w') as f:
                f.write('''<?xml version="1.0" encoding="UTF-8"?>
    <Settings>
        <ContentFolder>content</ContentFolder>
        <BaseUrl>http://www.roblox.com</BaseUrl>
    </Settings>
    ''')

        verPath = installdir / 'version.txt'
        if not verPath.exists():
            with verPath.open('w') as f:
                f.write(clientVersion)

    key = reg.CreateKeyEx(reg.HKEY_CLASSES_ROOT, r"roblox-player\shell\open\command")    
    reg.SetValueEx(key, None, 0, reg.REG_SZ, f'"{executable}" "%1"')
    reg.CloseKey(key)

if __name__ == '__main__':
    launch('app')