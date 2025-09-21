import customtkinter as tk
import tkinter as ntk
import winreg as reg
import sys
import threading
from util_toolbox import parse, themes, getasset, Font, cleanup, configpath, centerwindow, write, ConfigEntry
from launcher import silent_update
from customtkinter import set_appearance_mode
from tkinter import messagebox as mb
from PIL import Image

def config():
    try:
        main = tk.CTk()

        centerwindow(main, 400, 225)
        main.title('Configure Astra')
        main.resizable(False, False)

        config = parse(configpath)
        theme = config.get('Theme', 'Light')
        version = config.get('Version', 'x.x.x')
        font = config.get('Font', 'Inter')
        opengamestartup = config.get('OpenGameStartup', 'N')

        realtheme = theme

        globalmedium = Font.new(font,18)
        globalsmall = Font.new(font,12)

        if theme == 'System':
            import darkdetect
            if darkdetect.isDark():
                theme = 'Dark'
            else:
                theme = 'Light'

        set_appearance_mode(theme)
        main.configure(bg_color=themes[theme]['bg_color'])
        main.iconbitmap(getasset('logo', 'icon', theme))

        thread = threading.Thread(target=silent_update)

        thread.start()

        falsebg = ntk.Frame(master=main, background=themes[theme]['bg_color'])
        falsebg.pack(expand=True, fill='both')

        tabview = tk.CTkTabview(master=falsebg, fg_color=themes[theme]['bg_color'], bg_color=themes[theme]['bg_color'], corner_radius=14, segmented_button_selected_color='#538fd8', segmented_button_unselected_hover_color='#215da6', segmented_button_selected_hover_color='#215da6',)
        tabview._segmented_button.configure(font=globalsmall)
        tabview.pack(expand=True, fill='both', padx=10, pady=10)

        general = tabview.add('General')
        appearance = tabview.add('Appearance')
        about = tabview.add('About')

        # general tab

        generalscroll = tk.CTkScrollableFrame(general, width=400, fg_color=themes[theme]['bg_color'])
        generalscroll.pack()

        def startup(value):
            key = reg.OpenKeyEx(reg.HKEY_CURRENT_USER, r'Software\\Microsoft\Windows\\CurrentVersion\\Run', 0, reg.KEY_ALL_ACCESS)
            if value == True:
                reg.SetValueEx(key, 'Roblox', 0, reg.REG_EXPAND_SZ, f'"{sys.argv[0]}" --app')
            else:
                reg.DeleteValue(key, 'Roblox')

        openstartupbox = ConfigEntry(generalscroll, text='Open Roblox on Startup', type='switch', fg_color=themes[theme]['btn_color'], command=lambda: startup(openstartupbox.get()))
        openstartupbox.pack()
        
        opengamestartupbox = ConfigEntry(generalscroll, text='Open Game on Startup', type='switch', fg_color=themes[theme]['btn_color'], command=lambda: startup(openstartupbox.get()))
        opengamestartupbox.pack(pady=20)
        
        #appearance tab
        
        appearancescroll = tk.CTkScrollableFrame(appearance, width=400, fg_color=themes[theme]['bg_color'])
        appearancescroll.pack()

        themebox = ConfigEntry(appearancescroll, text='Application Theme', type='combobox', options=['Light','Dark','System'], fg_color=themes[theme]['btn_color'], setting=realtheme, command=lambda _: write(configpath, {'Theme': themebox.get()}))

        themebox.pack()

        # about tab
        logoimage = Image.open(getasset('logo', 'image', theme))
        logolabel = tk.CTkLabel(about, text='', image=tk.CTkImage(logoimage, size=(100, 100) if theme == 'Dark' else (85, 85)), bg_color=themes[theme]['bg_color'])
        logolabel.place(x=-5 if theme == 'Dark' else 0)

        logotext = tk.CTkLabel(about, text=f'Astra\n{version}',text_color=themes[theme]['ui_color'], font=globalmedium, bg_color=themes[theme]['bg_color'],justify='center')
        logotext.place(x=18,y=90)

        infotext = tk.CTkLabel(about, text='A Roblox bootstrapper', font=globalmedium)
        infotext.place(x=100, y=10)

        infotext2 = tk.CTkLabel(about, text='and indirectly, others', font=globalsmall)
        infotext2.place(x=100, y=60)

        infotext3 = tk.CTkLabel(about, text='By itstheguy4873', font=globalmedium)
        infotext3.place(x=100, y=40)

        infotext4 = tk.CTkLabel(about, text=f'Running at {__file__}', font=globalsmall, wraplength=280)
        infotext4.place(x=100, y=100)

        #notice
        mb.showinfo('Notice', "As Astra is *barely working,* the settings menu is incomplete and probably won't work.")

        main.mainloop()

        cleanup()
    except Exception as e:
        mb.showerror('Astra', f'Astra encountered an error: {e}')

if __name__ == '__main__': #debug thing
    config()
