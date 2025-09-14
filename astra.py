import customtkinter as tk
import tkinter as ntk
from util_toolbox import parse, themes, getasset, setfont, cleanup, configpath, centerwindow
from customtkinter import set_appearance_mode
from PIL import Image
from config import config
from launcher import launch
import sys
import darkdetect
import logging

logging.basicConfig(level=logging.DEBUG)

if len(sys.argv) > 1:
    uri = sys.argv[1]
    
    if uri == '--config'.lower():
        config()
    if uri == '--app'.lower():
        launch('app')

pconfig = parse(configpath)
theme = pconfig.get('Theme', 'Light')
version = pconfig.get('Version', 'x.x.x')
font = pconfig.get('Font', 'Inter')

globalfont = setfont(font,24)
btnfont = setfont(font,18)

if theme == 'System':
    if darkdetect.isDark():
        theme = 'Dark'
    else:
        theme = 'Light'

main = tk.CTk()
centerwindow(main, 400, 150)
main.title('Astra')
main.resizable(False, False)

set_appearance_mode(theme)
main.configure(bg_color=themes[theme]['bg_color'])
main.iconbitmap(getasset('logo', 'icon', theme))

falsebg = ntk.Frame(master=main, background=themes[theme]['bg_color']) #i hate windows 11
falsebg.pack(expand=True, fill='both')

logoimage = Image.open(getasset('logo', 'image', theme))
logoimagetk = tk.CTkImage(logoimage, size=(100, 100) if theme == 'Dark' else (85, 85))
logolabel = tk.CTkLabel(main, text='', image=logoimagetk, bg_color=themes[theme]['bg_color']) #resize the images manually? NOPE
logolabel.place(x=220, y=25)

logotext = tk.CTkLabel(main, text='Astra',text_color=themes[theme]['ui_color'], font=globalfont, bg_color=themes[theme]['bg_color'],justify='left')
vertext = tk.CTkLabel(main, text=version,text_color='#a5a5a5', font=btnfont, bg_color=themes[theme]['bg_color'],justify='left')
logotext.place(x=320,y=40)
vertext.place(x=330,y=70)

fadejob = None

def hextorgb(hexcolor):
    return tuple(int(hexcolor[i:i+2], 16) for i in (1, 3, 5))

def rgbtohex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

def fade(button, targetcolor, steps=20, delay=25):
    if not hasattr(button, 'fadejob'):
        button.fadejob = None
    
    if button.fadejob:
        button.after_cancel(button.fadejob)
    
    initialcolor = button.cget("fg_color")
    initialrgb = hextorgb(initialcolor)
    targetrgb = hextorgb(targetcolor)

    def updatecolor(step):
        r = int(initialrgb[0] + (targetrgb[0] - initialrgb[0]) * step / steps)
        g = int(initialrgb[1] + (targetrgb[1] - initialrgb[1]) * step / steps)
        b = int(initialrgb[2] + (targetrgb[2] - initialrgb[2]) * step / steps)
        button.configure(fg_color=rgbtohex(r, g, b))
        if step < steps:
            button.fadejob = button.after(delay, updatecolor, step + 1)

    updatecolor(0)


def onhover(button, hovercolor):
    fade(button, hovercolor, 5, 10)

def onleave(button, initialcolor):
    fade(button, initialcolor, 5, 10)

def launchroblox():
    main.destroy()
    launch('roblox')

def launchsettings():
    main.destroy()
    config()

openroblox = tk.CTkButton(main, text='Open Roblox', command=lambda: launchroblox, width=150, height=40, font=btnfont, text_color=themes[theme]['ui_color'], bg_color=themes[theme]['bg_color'], fg_color = themes[theme]['bg_color'],border_color=themes[theme]['hover_color'], border_width=1.5, corner_radius=10, hover_color=themes[theme]['hover_color'])
openroblox.place(x=25,y=15)

configbutton = tk.CTkButton(main, text='Configure Astra', command=launchsettings, width=150, height=40, font=btnfont, text_color=themes[theme]['ui_color'], bg_color=themes[theme]['bg_color'], fg_color = themes[theme]['bg_color'],border_color=themes[theme]['hover_color'], border_width=1.5, corner_radius=10, hover_color=themes[theme]['hover_color'])
configbutton.place(x=25,y=75)

openroblox.bind("<Enter>", lambda x: onhover(openroblox, themes[theme]['hover_color']))
openroblox.bind("<Leave>", lambda x: onleave(openroblox, themes[theme]['bg_color']))

configbutton.bind("<Enter>", lambda x: onhover(configbutton,themes[theme]['hover_color']))
configbutton.bind("<Leave>", lambda x: onleave(configbutton, themes[theme]['bg_color']))

main.mainloop()

cleanup()