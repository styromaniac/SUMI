#!/bin/bash

# Prompt for action
echo "Do you wish to install or uninstall? (i/u)"
read action

# Detect the OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_NAME="macos"
else
    OS_NAME=$(grep -oP '^ID=\K.*' /etc/os-release | tr -d '"')
fi

# Set fallback directory values if unset
if [ -z "$XDG_DATA_HOME" ]; then
    XDG_DATA_HOME="$HOME/.local/share"
fi

if [ -z "$XDG_CONFIG_HOME" ]; then
    XDG_CONFIG_HOME="$HOME/.config"
fi

# Script config
script_name="SUMI.py"
icon_name="Sumi.png"

# Install directories
if [ "$OS_NAME" == "macos" ]; then
    install_dir="/Applications"
    icon_dir="$HOME/Library/Application Support/SUMI"
else
    install_dir="$HOME/Applications"
    icon_dir="$XDG_DATA_HOME/icons"
    desktop_dir="$XDG_DATA_HOME/applications"
fi

# Function definitions
copy_file() {
    cp "$1" "$2" || {
        echo "Failed copying $1 to $2"
        exit 1
    }
}

remove_file() {
    rm -f "$1" || {
        echo "Failed removing $1"
        exit 1
    }
}

create_desktop_entry() {
    cat <<EOF > "$1"
[Desktop Entry]
Name=SUMI
Exec=$install_dir/$script_name
Icon=$icon_dir/$icon_name
Type=Application
Categories=Game;
EOF
}

install_dependencies() {
    echo "Installing system dependencies..."
    case $OS_NAME in
        "ubuntu"|"debian")
            sudo apt-get update
            sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-pip -y
            ;;
        "fedora")
            sudo dnf install python3-gobject python3-cairo-gobject gtk3 python3-pip -y
            ;;
        "arch"|"manjaro")
            sudo pacman -Syu --noconfirm
            sudo pacman -S python-gobject python-cairo gtk3 python-pip --noconfirm
            ;;
        "opensuse")
            sudo zypper refresh
            sudo zypper install python3-gobject python3-gobject-cairo gtk3 python3-pip -y
            ;;
        "centos")
            sudo yum install python3-gobject python3-cairo-gobject gtk3 python-pip -y
            ;;
        "gentoo")
            sudo emerge --sync
            sudo emerge dev-python/pygobject:3 x11-libs/gtk+:3 dev-python/pip
            ;;
        "nixos")
            sudo nix-channel --update
            nix-env -iA nixos.python3 nixos.gtk3 nixos.python3Packages.gobject-introspection nixos.python3Packages.pygobject3 nixos.python3Packages.requests
            ;;
        "macos")
            brew install python3
            brew install pygobject3 gtk+3
            ;;
        *)
            echo "Manual installation of dependencies might be required for your OS."
            ;;
    esac

    # Install Python modules, skip if OS is SteamOS
    if [ "$OS_NAME" != "steamos" ]; then
        echo "Installing Python modules..."
        pip install requests PyGObject
    else
        echo "Skipping Python modules installation on SteamOS."
    fi
}

# Main install logic
if [ "$action" == "i" ]; then
    install_dependencies
    echo "Installing SUMI..."
    mkdir -p "$install_dir"
    copy_file "$script_name" "$install_dir"
    chmod +x "$install_dir/$script_name"
    mkdir -p "$icon_dir"
    copy_file "$icon_name" "$icon_dir"
    if [ "$OS_NAME" != "macos" ]; then
        create_desktop_entry "$desktop_dir/SUMI.desktop"
    fi
    echo "Installed to $install_dir/$script_name"
elif [ "$action" == "u" ]; then
    echo "Uninstalling SUMI..."
    remove_file "$install_dir/$script_name"
    remove_file "$icon_dir/$icon_name"
    if [ "$OS_NAME" != "macos" ]; then
        remove_file "$desktop_dir/SUMI.desktop"
    fi
    echo "SUMI has been uninstalled."
else
    echo "Invalid action selected. Please run the script again and type 'i' or 'u'."
    exit 1
fi
