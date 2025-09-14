import customtkinter as tk
import tkinter as ntk
import requests
import os
import shutil
import logging
import zipfile
import io
import psutil
import pythoncom
import sys
import winreg as reg
import xml.etree.ElementTree as ET
from util_toolbox import themes, parse, configpath, cleanup, getasset, setfont, extractroots, centerwindow
from subprocess import Popen
from PIL import Image
from customtkinter import set_appearance_mode
from pathlib import Path
from win32com.shell import shell # type: ignore
from tkinter import messagebox as mb

logging.getLogger('requests').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

def launch(mode='app'):
    try:
        config = parse(configpath)
        theme = config.get('Theme', 'Light')
        font = config.get('Font', 'Inter')
        
        globalfont = setfont(font,15)

        main = tk.CTkToplevel()
        centerwindow(main, 400, 225)
        main.title('Astra')
        main.resizable(False, False)
        main.iconbitmap(getasset('logo', 'icon', theme))

        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == 'RobloxPlayerBeta.exe'.lower() or proc.info['name'] and proc.info['name'].lower() == 'RobloxStudioBeta.exe'.lower():
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        falsebg = ntk.Frame(master=main, background=themes[theme]['bg_color'])
        falsebg.pack(expand=True, fill='both')

        logoimage = Image.open(getasset('logo', 'image', theme))
        logoimagetk = tk.CTkImage(logoimage, size=(100, 100) if theme == 'Dark' else (85, 85))
        logolabel = tk.CTkLabel(main, text='', image=logoimagetk, bg_color=themes[theme]['bg_color'])
        logolabel.place(x=155,y=20)

        statustext = tk.CTkLabel(main, text='Status', font=globalfont, bg_color=themes[theme]['bg_color'], width=100)
        statustext.place(x=200,y=125, anchor='center')

        statuslabel = tk.CTkProgressBar(main, mode='indeterminate')
        statuslabel.place(x=100,y=175)
        statuslabel.start()

        set_appearance_mode(theme)
        main.configure(bg_color=themes[theme]['bg_color'])

        #this wasn't fun to code

        response = requests.get('https://clientsettingscdn.roblox.com/v2/client-version/WindowsPlayer')
        if response.status_code == 200:
            data = response.json()
            rlatestver = data.get('clientVersionUpload', 'NotFound')
        else:
            mb.showerror('Error', 'Failed to fetch version information.')
            cleanup()

        fverurlbase = f'https://setup.rbxcdn.com/{rlatestver}-'

        rbxpath = Path(os.environ.get('LOCALAPPDATA')) / 'Roblox'

        main.update()

        installdir = rbxpath / 'RobloxPlayer'
        installdir.mkdir(exist_ok=True)

        if Path.exists(rbxpath / 'Versions'):
            shutil.rmtree(rbxpath / 'Versions')

        for key, value in extractroots.items():
            response = requests.get(f'{fverurlbase}{key}')
            if response.status_code == 200:
                zipbytes = io.BytesIO(response.content)
                main.after(0, lambda: statustext.configure(text=f'Extract {key}'))
                main.update()

                with zipfile.ZipFile(zipbytes) as zip_file:
                    zipdir = installdir / value
                    zipdir.mkdir(parents=True, exist_ok=True)

                    zip_file.extractall(zipdir)

        astrapath = Path(sys.argv[0]).resolve()

        main.after(0, lambda: statustext.configure(text='Configure Registry'))
        key1 = reg.OpenKeyEx(reg.HKEY_CURRENT_USER, r'Software\ROBLOX Corporation\Environments\roblox-player', 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key1, 'clientExe', 0, reg.REG_SZ, str(astrapath))
        reg.SetValueEx(key1, 'version', 0, reg.REG_SZ, rlatestver)
        reg.SetValueEx(key1, None, 0, reg.REG_SZ, str(astrapath))

        key2 = reg.OpenKeyEx(reg.HKEY_CURRENT_USER, r'Software\ROBLOX Corporation\Environments\roblox-player\Capabilities', 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key2, 'ApplicationIcon', 0, reg.REG_EXPAND_SZ, f'"{str(astrapath)}",0')
        reg.CloseKey(key2)

        key3 = reg.OpenKeyEx(reg.HKEY_CLASSES_ROOT, r'roblox-player\shell\open\command', 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key3, 'version', 0, reg.REG_SZ, rlatestver)
        reg.SetValueEx(key3, None, 0, reg.REG_SZ, f'"{str(astrapath)}" %1')
        reg.CloseKey(key3)

        logging.info('Successfully wrote registry')

        pythoncom.CoInitialize()
        shelllink = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)

        shelllink.SetPath(str(installdir / 'RobloxPlayerBeta.exe'))
        shelllink.SetArguments('roblox-player:1+launchmode:app')
        shelllink.SetWorkingDirectory(os.path.dirname(str(installdir / 'RobloxPlayerBeta.exe')))
        shelllink.SetIconLocation(str(installdir / 'RobloxPlayerBeta.exe'), 0)

        persistfile = shelllink.QueryInterface(pythoncom.IID_IPersistFile)
        lnk = str(Path(os.environ.get('APPDATA')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Roblox' / 'Roblox Player.lnk')
        persistfile.Save(lnk, 0)

        appsettingsxml = installdir / 'AppSettings.xml'
        settingsxml = ET.Element('Settings')
        contentfolderxml = ET.SubElement(settingsxml, 'ContentFolder')
        contentfolderxml.text = 'content'
        baseurlxml = ET.SubElement(settingsxml, 'BaseUrl')
        baseurlxml.text = 'http://www.roblox.com'

        tree = ET.ElementTree(settingsxml)
        tree.write(appsettingsxml, encoding='utf-8', xml_declaration=False)

        if mode == 'app':
            proc = Popen([str(installdir / 'RobloxPlayerBeta.exe'), '--app'])
        if mode.startswith('roblox'):
            proc = Popen([str(installdir / 'RobloxPlayerBeta.exe'), mode])

        main.withdraw()

        main.mainloop()

        cleanup()
    
    except Exception as e:
        mb.showerror('Astra', f'Astra encountered an error: {e}')

def silent_update():
    try:
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == 'RobloxPlayerBeta.exe'.lower():
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        response = requests.get('https://clientsettingscdn.roblox.com/v2/client-version/WindowsPlayer')
        if response.status_code == 200:
            data = response.json()
            rlatestver = data.get('clientVersionUpload', 'NotFound')
        else:
            mb.showerror('Error', 'Failed to fetch version information.')
            cleanup()

        fverurlbase = f'https://setup.rbxcdn.com/{rlatestver}-'

        rbxpath = Path(os.environ.get('LOCALAPPDATA')) / 'Roblox'

        installdir = rbxpath / 'RobloxPlayer'
        installdir.mkdir(exist_ok=True)

        if Path.exists(rbxpath / 'Versions'):
            shutil.rmtree(rbxpath / 'Versions')

        for key, value in extractroots.items():
            response = requests.get(f'{fverurlbase}{key}')
            if response.status_code == 200:
                zipbytes = io.BytesIO(response.content)
                with zipfile.ZipFile(zipbytes) as zip_file:
                    zipdir = installdir / value
                    zipdir.mkdir(parents=True, exist_ok=True)

                    zip_file.extractall(zipdir)

        astrapath = Path(sys.argv[0]).resolve()

        key1 = reg.OpenKeyEx(reg.HKEY_CURRENT_USER, r'Software\ROBLOX Corporation\Environments\roblox-player', 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key1, 'clientExe', 0, reg.REG_SZ, str(astrapath))
        reg.SetValueEx(key1, 'version', 0, reg.REG_SZ, rlatestver)
        reg.SetValueEx(key1, None, 0, reg.REG_SZ, str(astrapath))

        key2 = reg.OpenKeyEx(reg.HKEY_CURRENT_USER, r'Software\ROBLOX Corporation\Environments\roblox-player\Capabilities', 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key2, 'ApplicationIcon', 0, reg.REG_EXPAND_SZ, f'"{str(astrapath)}",0')
        reg.CloseKey(key2)

        key3 = reg.OpenKeyEx(reg.HKEY_CLASSES_ROOT, r'roblox-player\shell\open\command', 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key3, 'version', 0, reg.REG_SZ, rlatestver)
        reg.SetValueEx(key3, None, 0, reg.REG_SZ, f'"{str(astrapath)}" %1')
        reg.CloseKey(key3)

        logging.info('Successfully wrote registry')

        pythoncom.CoInitialize()
        shelllink = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)

        shelllink.SetPath(str(installdir / 'RobloxPlayerBeta.exe'))
        shelllink.SetArguments('roblox-player:1+launchmode:app')
        shelllink.SetWorkingDirectory(os.path.dirname(str(installdir / 'RobloxPlayerBeta.exe')))
        shelllink.SetIconLocation(str(installdir / 'RobloxPlayerBeta.exe'), 0)

        persistfile = shelllink.QueryInterface(pythoncom.IID_IPersistFile)
        lnk = str(Path(os.environ.get('APPDATA')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Roblox' / 'Roblox Player.lnk')
        persistfile.Save(lnk, 0)

        appsettingsxml = installdir / 'AppSettings.xml'
        settingsxml = ET.Element('Settings')
        contentfolderxml = ET.SubElement(settingsxml, 'ContentFolder')
        contentfolderxml.text = 'content'
        baseurlxml = ET.SubElement(settingsxml, 'BaseUrl')
        baseurlxml.text = 'http://www.roblox.com'

        tree = ET.ElementTree(settingsxml)
        tree.write(appsettingsxml, encoding='utf-8', xml_declaration=False)
    
    except Exception as e:
       pass
    


if __name__ == '__main__':
    launch('app')