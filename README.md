<img width="824" height="303" src="https://github.com/user-attachments/assets/d6aaf93f-d522-4df2-8e84-92631d7284a9#gh-light-mode-only"/>
<img width="824" height="303" src="https://github.com/user-attachments/assets/80e491ae-3f95-4dd4-ad70-99fd5a811e88#gh-dark-mode-only" />

# About

Astra is a custom bootstrapper for [Roblox](https://roblox.com) designed to provide handy features that aren't officially available.
> [!CAUTION]
> This repository is the **ONLY** official source for Astra! In the near future, there will be an official site.

# Installation

You can get Astra from the [latest release.](https://github.com/itstheguy4873/astra-roblox/releases/latest)

Astra is available for Windows only. I don't have any plans to support other OSes anytime soon.

> [!NOTE]
> If SmartScreen flags Astra as malicious, you can safely disregard this warning.
> This is likely because its an unknown program.
> Astra is **not malware of any kind,** and its source code is available for auditing.

# Building

If you want to build Astra, you can do so with `git` and `PyInstaller` with the following:

```
git clone https://github.com/itstheguy4873/astra-roblox
cd astra-roblox
```

And then package it with:

```
pyinstaller --noconfirm --onedir --windowed --icon ".\assets\icon\light\logo.ico" --name "Astra" --add-data ".\config.py;." --add-data ".\util_toolbox.py;." --add-data ".\launcher.py;." --add-data ".\assets;assets/"  ".\astra.py" --distpath .
```

# Note

Astra is in early development, and some features may not work as intended.
If you encounter any problems, then feel free to open an [issue.](https://github.com/itstheguy4873/astra-roblox/issues)
