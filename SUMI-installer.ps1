# Prompt for action
$action = Read-Host "Do you wish to install or uninstall? (i/u)"

# Script config
$scriptName = "SUMI.py"
$iconName = "Sumi.png"

# Install directories
$installDir = Join-Path $env:APPDATA "SUMI"
$iconDir = $installDir

# Function definitions
function Copy-File {
    param($source, $destination)
    Copy-Item $source $destination -ErrorAction Stop
    if ($?) {
        Write-Host "Copied $source to $destination"
    } else {
        Write-Host "Failed copying $source to $destination"
        exit 1
    }
}

function Remove-File {
    param($file)
    Remove-Item $file -ErrorAction SilentlyContinue
    if ($?) {
        Write-Host "Removed $file"
    } else {
        Write-Host "Failed removing $file"
    }
}

function Install-Dependencies {
    Write-Host "Installing system dependencies..."
    
    # Install Python if not already installed
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Host "Python not found. Installing Python..."
        # Download the Python installer
        $pythonInstallerUrl = "https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe"
        $pythonInstallerPath = Join-Path $env:TEMP "python-installer.exe"
        Invoke-WebRequest -Uri $pythonInstallerUrl -OutFile $pythonInstallerPath

        # Install Python silently
        Start-Process -FilePath $pythonInstallerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait

        # Refresh the PATH environment variable
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }

    # Install Python modules
    Write-Host "Installing Python modules..."
    pip install requests PyGObject
}

# Main install logic
if ($action -eq "i") {
    Install-Dependencies
    Write-Host "Installing SUMI..."
    New-Item -ItemType Directory -Force -Path $installDir | Out-Null
    Copy-File $scriptName $installDir
    Copy-File $iconName $iconDir
    Write-Host "Installed to $installDir\$scriptName"
} elseif ($action -eq "u") {
    Write-Host "Uninstalling SUMI..."
    Remove-File "$installDir\$scriptName"
    Remove-File "$iconDir\$iconName"
    Write-Host "SUMI has been uninstalled."
} else {
    Write-Host "Invalid action selected. Please run the script again and type 'i' or 'u'."
    exit 1
}
