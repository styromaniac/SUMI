<img src="https://raw.githubusercontent.com/styromaniac/SUMI/main/Sumi.png" width="256">

# Suyu Update Manager and Installer (SUMI)

A robust, code-readable Suyu installer/updater for Steam on SteamOS and other Linux distros using [Suyu's releases](https://git.suyu.dev/suyu/suyu/releases). The purpose of this script is to save the user's time by being more easily accessible, convenient, logical, and informative. It is usable through Gaming Mode In SteamOS 3, Bazzite, ChimeraOS, Garuda Linux, HoloISO, Nobara Linux Steam Deck Edition, and more.

SUMI will not redownload the same revision of Suyu-ea.AppImage that's already installed. The prior installed revision will be backed up and will be sourced from its backup file instead of redownloaded if it's reinstalled, saving bandwidth.

## Install System Dependencies
First, install the necessary system dependencies for your specific Linux distribution if SUMI doesn't work already:

### Debian/Ubuntu (apt)
```bash
sudo apt-get update
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

### Fedora (dnf)
```bash
sudo dnf install python3-gobject python3-cairo-gobject gtk3
```

### Arch Linux (pacman)
```bash
sudo pacman -Syu
sudo pacman -S python-gobject python-cairo gtk3
```

### openSUSE (zypper)
```bash
sudo zypper refresh
sudo zypper install python3-gobject python3-gobject-cairo gtk3
```

### CentOS (yum)
For CentOS 7:
```bash
sudo yum install python3-gobject python3-cairo-gobject gtk3
```
For CentOS 8, you might need to enable EPEL and PowerTools repositories, and the package names could be slightly different. 

### Gentoo (emerge)
```bash
sudo emerge --sync
sudo emerge dev-python/pygobject:3 x11-libs/gtk+:3
```

### NixOS (nix)
```bash
sudo nix-channel --update
nix-env -iA nixos.python3 nixos.gtk3 nixos.python3Packages.gobject-introspection nixos.python3Packages.pygobject3 nixos.python3Packages.requests
```

## Install pip
Next, install `pip`, the Python package manager, on your distribution:

### Debian/Ubuntu (apt)
```bash
sudo apt-get update
sudo apt-get install python3-pip
```

### Fedora (dnf)
```bash
sudo dnf install python3-pip
```

### Arch Linux (pacman)
```bash
sudo pacman -Syu
sudo pacman -S python-pip
```

### openSUSE (zypper)
```bash
sudo zypper refresh
sudo zypper install python3-pip
```

### CentOS (yum)
For CentOS 7:
```bash
sudo yum install epel-release
sudo yum install python-pip
```
For CentOS 8:
```bash
sudo dnf install python3-pip
```

### Gentoo (emerge)
```bash
sudo emerge --sync
sudo emerge dev-python/pip
```

### NixOS (nix)
```bash
nix-env -iA nixos.python3Packages.pip
```

Note:
- For CentOS 7, the EPEL (Extra Packages for Enterprise Linux) repository is required to install `pip`.
- CentOS 8 and newer versions use `dnf` as the default package manager.
- Always ensure your system's package index is up-to-date (`update`, `refresh`, `--sync`) before installing new packages.

## Install Python3 Modules
Finally, use `pip` to install the required Python modules:

```
pip install requests PyGObject
```
---

## Extracting and Running the Installer Script

If you have downloaded `SUMI-main.zip`, you will need to extract it and then make the installer script executable to run it on your system. Follow these steps:

1. **Navigate to the Download Location**: Open a terminal and navigate to the directory where `SUMI-main.zip` is located. For example, if it's in the `Downloads` folder, use:
    ```bash
    cd ~/Downloads
    ```

2. **Unzip the Archive**: Extract the contents of the ZIP file with the following command:
    ```bash
    unzip SUMI-main.zip
    ```

3. **Navigate to the Extracted Folder**: Change directory to the extracted folder. It's typically named after the ZIP file:
    ```bash
    cd SUMI-main
    ```

4. **Make the Installer Script Executable**: Run the following command to make `SUMI-installer.sh` executable:
    ```bash
    chmod +x SUMI-installer.sh
    ```

5. **Run the Installer**: Now, you can execute the script with:
    ```bash
    ./SUMI-installer.sh
    ```

This process involves changing the script's permissions to allow it to be run as a program on your Linux system. The `chmod +x` command is used for this purpose.
---
## Compiling SUMI.py for Your Distribution
### 1. Install PyInstaller
First, you need to install PyInstaller. It's recommended to do this in a virtual environment to avoid conflicts with system packages.

```bash
# Create a virtual environment (optional but recommended)
python3 -m venv sumi_env
source sumi_env/bin/activate

# Install PyInstaller
pip install pyinstaller
```

### 2. Prepare Your Script
Make sure the script `SUMI.py` is ready and tested. All dependencies should be correctly imported in the script.

### 3. Build the Binary
Navigate to the directory where `SUMI.py` is located and run PyInstaller:

```bash
cd /path/to/your/script
pyinstaller --onefile SUMI.py
```

The `--onefile` option tells PyInstaller to pack everything into a single executable file. After the process completes, you'll find the binary in the `dist` directory.

### 4. Make the Binary Executable

```
chmod +x SUMI
```

### 5. Test the Binary
It's important to test the binary to make sure it runs correctly:

```bash
./dist/SUMI
```

### Notes:
- SUMI-installer.sh already exists to install SUMI.py and is recommended for simple installation and consistency in behavior, compatibility, performance and stability.
- The binary built with PyInstaller is specific to the OS and architecture you build it on. If you build it on Ubuntu, it's meant for Ubuntu systems, and similarly for other distributions.
- If your distribution of SUMI depends on non-Python files (like images, data files, etc.), you need to tell PyInstaller to include these files. Check PyInstaller's documentation for more on this.
- Building a binary does not always guarantee the same performance or behavior as running the script directly with Python. Be sure to thoroughly test the binary on the target system.

### Optional: Creating a Desktop Entry
If you want to integrate SUMI with the Linux desktop environments, you can create a `.desktop` file:

```ini
[Desktop Entry]
Name=SUMI
Exec=/path/to/dist/SUMI
Icon=/path/to/Sumi.png
Type=Application
Categories=Utility;
```

Replace `/path/to/dist/SUMI` with the actual path to the executable and `/path/to/Sumi.png` with the path to an icon of your choice. This file should be placed in `~/.local/share/applications/` or `/usr/share/applications/` for system-wide availability.

By following these steps, you should be able to create a binary for SUMI that can be distributed and run on Linux systems.
