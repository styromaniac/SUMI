# Suyu Update Manager and Installer (SUMI)

SUMI is a robust, code-readable Suyu installer/updater for Steam on SteamOS and various Linux distributions, macOS and Windows. Designed to enhance user convenience by being accessible, logical, and informative, SUMI supports automatic detection of compatible operating systems plus CPU architectures and optimizes bandwidth by avoiding unnecessary redownloads of suyu.

![SUMI Logo](https://raw.githubusercontent.com/styromaniac/SUMI/main/Sumi.png)

## Features

- Prevents unnecessary redownloads of Suyu, saving bandwidth.
- Backs up previously installed revisions for reuse, conserving resources.
- Detects OSes and CPU architectures automatically.
- Compatible with a wide range of Linux distributions, including SteamOS 3, Bazzite, ChimeraOS, Garuda Linux, HoloISO, Nobara Linux Steam Deck Edition, and more.

## System Requirements

SUMI supports various Linux distributions and provides guidance for MacOS and Windows, extending its utility across different operating systems.

## Install System Dependencies

### Linux

#### Debian/Ubuntu (apt)
```bash
sudo apt-get update
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

#### Fedora (dnf)
```bash
sudo dnf install python3-gobject python3-cairo-gobject gtk3
```

#### Arch Linux (pacman)
```bash
sudo pacman -Syu
sudo pacman -S python-gobject python-cairo gtk3
```

#### openSUSE (zypper)
```bash
sudo zypper refresh
sudo zypper install python3-gobject python3-gobject-cairo gtk3
```

#### CentOS (yum)
For CentOS 7:
```bash
sudo yum install python3-gobject python3-cairo-gobject gtk3
```
For CentOS 8 and newer versions:
```bash
sudo dnf install python3-gobject python3-cairo-gobject gtk3
```

#### Gentoo (emerge)
```bash
sudo emerge --sync
sudo emerge dev-python/pygobject:3 x11-libs/gtk+:3
```

#### NixOS (nix)
```bash
sudo nix-channel --update
nix-env -iA nixos.python3 nixos.gtk3 nixos.python3Packages.gobject-introspection nixos.python3Packages.pygobject3 nixos.python3Packages.requests
```

### MacOS

MacOS users will need to install Python3 and relevant dependencies using Homebrew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python3 gtk+3
```

### Windows

Ensure Python3 is installed from the official Python website or through the Microsoft Store. During installation, select the option to add Python to PATH.

## Install pip

Pip is essential for installing additional Python packages required by SUMI.

### Linux

Use the package manager specific to your distribution to install pip.

### MacOS

Pip is included with the Python installation via Homebrew.

### Windows

Pip is included with Python installation. Verify its installation by running `pip --version` in Command Prompt or PowerShell.

## Install Python3 Modules

Across all platforms, use pip to install the required Python modules:

```bash
pip install requests PyGObject
```

Note: Installing PyGObject on MacOS and Windows may require additional steps due to GTK dependencies.

## Extracting and Running the Installer Script

### Linux

Navigate to the directory where `SUMI-main.zip` is downloaded, unzip it, change the directory to the extracted folder, make the installer script executable, and run it:

```bash
cd ~/Downloads
unzip SUMI-main.zip
cd SUMI-main
chmod +x SUMI-installer.sh
./SUMI-installer.sh
```

### MacOS

After downloading `SUMI-main.zip`, extract it, navigate to the `SUMI-main` directory in your terminal, and execute the installer script:

```bash
unzip SUMI-main.zip -d SUMI-main
cd SUMI-main
./SUMI-installer.sh
```

### Windows

Download and extract `SUMI-main.zip`, then run the installer script through Command Prompt or PowerShell:

```cmd
cd path\to\SUMI-main
.\SUMI-installer.ps1
```

Ensure you navigate to the directory where `SUMI-main` is extracted before running the installer script.

## Compiling SUMI.py for Your Distribution

To compile `SUMI.py` into a standalone application or script, use PyInstaller or a similar tool. This process involves using PyInstaller to generate a single executable file, which can simplify the distribution and execution of SUMI on various systems.

### Linux

1. Install PyInstaller via pip:

```bash
pip install pyinstaller
```

2. Navigate to the directory containing `SUMI.py` and run PyInstaller:

```bash
pyinstaller --onefile SUMI.py
```

3. The executable will be located in the `dist` directory within your project folder.

### MacOS

MacOS users should follow the same steps as Linux for compiling `SUMI.py`. However, you might need to address permissions or security prompts due to MacOS's Gatekeeper feature:

1. Install PyInstaller using pip:

```bash
pip3 install pyinstaller
```

2. Compile `SUMI.py` into a standalone application:

```bash
pyinstaller --onefile SUMI.py
```

3. If you encounter a security prompt when running the executable, navigate to `System Preferences > Security & Privacy` and allow the app to run, or right-click the app and select `Open` for the first launch.

### Windows

On Windows, the process to compile `SUMI.py` is similar but ensure your command prompt or PowerShell has access to Python and PyInstaller:

1. Install PyInstaller through pip:

```cmd
pip install pyinstaller
```

2. Navigate to the directory containing `SUMI.py` and execute PyInstaller:

```cmd
pyinstaller --onefile SUMI.py
```

3. Find the compiled `.exe` in the `dist` directory. You can distribute this executable to other Windows users, allowing them to run SUMI without installing Python.

### Note

- The `--onefile` flag with PyInstaller creates a single bundled executable file for easy distribution.
- Users may need to install additional dependencies or runtime libraries depending on the specific requirements of SUMI and the target operating system.
- Testing the executable on different systems or virtual machines is recommended to ensure compatibility and functionality across various configurations.

## Optional: Creating a Desktop Entry (Linux) / Application Shortcut (MacOS and Windows)

For easier access to SUMI, you might want to create a desktop shortcut or entry.

### Linux

Create a `.desktop` file in `~/.local/share/applications/` with the following contents, adjusting paths as necessary:

```ini
[Desktop Entry]
Type=Application
Name=SUMI
Exec=/path/to/SUMI
Icon=/path/to/sumi_icon.png
Comment=Update Manager for Suyu
Categories=Utility;
```

### MacOS

To create an application shortcut, you might use Automator to create a small application that runs the SUMI script, or manually create a shortcut.

### Windows

Right-click on your desktop or in any folder where you want the shortcut, select `New > Shortcut`, and follow the prompts to create a shortcut to the SUMI executable. You can specify the path to the SUMI `.exe` file you generated with PyInstaller.
