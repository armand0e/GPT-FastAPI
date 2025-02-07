import os
import subprocess
import platform
import time
import sys
"""Ensures all Python dependencies are installed."""
print("📦 Checking and installing Python dependencies...")

try:
    result = subprocess.Popen([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], capture_output=True, text=True)
    if result.returncode == 0:
        
        print("✅ Python dependencies installed successfully.")
    else:
        raise Exception("⚠️ Failed to install dependencies. Please check your Python & Pip installation.")
except Exception as e:
    print(str(e))
    print(result.stderr)
    quit()

import dotenv

# Load existing .env file
dotenv.load_dotenv(dotenv_path="./src/.env")

SYSTEM = platform.system()

def get_git_bash_path():
    """Finds the path to Git Bash on Windows by intelligently searching for bash.exe."""
    
    # Step 1: Try the default installation path
    default_path = r"C:\Program Files\Git\bin\bash.exe"
    if os.path.exists(default_path):
        return default_path

    # Step 2: Use 'where git' to locate git.exe
    try:
        git_check = subprocess.run(["where", "git"], capture_output=True, text=True)
        git_path = git_check.stdout.strip().split("\n")[0]  # Get first match
    except Exception:
        git_path = None

    if git_path and os.path.exists(git_path):
        # Step 3: Traverse backward until we find the "Git" root folder
        git_parent = git_path
        while git_parent and os.path.basename(git_parent).lower() != "git":
            git_parent = os.path.dirname(git_parent)  # Go up one directory

        # Step 4: Recursively search inside "Git/" for "bash.exe"
        if os.path.exists(git_parent):
            for root, _, files in os.walk(git_parent):
                if "bash.exe" in files:
                    return os.path.join(root, "bash.exe")

    # Step 5: Last attempt—check Windows Registry
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\GitForWindows") as key:
            install_path = winreg.QueryValueEx(key, "InstallPath")[0]
            git_parent = install_path

            # Search inside registry path for bash.exe
            for root, _, files in os.walk(git_parent):
                if "bash.exe" in files:
                    return os.path.join(root, "bash.exe")
    except FileNotFoundError:
        print("⚠️ Git Bash not found. Installing Git now...")
        return None

def install_git_bash():
    """Uses Winget to install Git Bash silently, then finds its installation path."""
    print("🚀 Installing Git Bash via Winget...")
    install_command = (
        'winget install --exact --silent --force --disable-interactivity '
        '--accept-source-agreements --accept-package-agreements '
        '--id=Git.Git --source=winget '
        '--custom="/SP- /VERYSILENT /SUPPRESSMSGBOXES /NORESTART '
        '/NOCLOSEAPPLICATIONS /COMPONENTS=ext,ext\\shellhere,ext\\guihere,'
        'gitlfs,assoc,assoc_sh,scalar,windowsterminal"'
    )

    result = subprocess.run(install_command, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Git Bash installed successfully.")
        time.sleep(5)  # Give time for system updates
        return get_git_bash_path()
    else:
        print("❌ Git Bash installation failed. Check Winget availability.")
        print(result.stderr)
        quit()
        return None

def set_env_variable(env_path, key, value):
    """Writes or updates a key-value pair in the .env file."""
    dotenv.set_key(env_path, key, value)
    print(f"✅ Set {key} in {env_path}: {value}")

# 🖥️ Windows: Use Git Bash
if SYSTEM == "Windows":
    git_bash_path = get_git_bash_path()

    if not git_bash_path:
        git_bash_path = install_git_bash()

    if git_bash_path:
        set_env_variable("src/.env", "SHELL", git_bash_path)
    else:
        print("⚠️ Git Bash setup failed. Defaulting to PowerShell.")
        set_env_variable("./src/.env", "SHELL", "powershell.exe")

# 🍏 Mac & 🐧 Linux: Use /bin/bash
elif SYSTEM in ["Darwin", "Linux"]:
    set_env_variable("./src/.env", "SHELL", "/bin/bash")

# 🏠 Setup Port
port = input("Enter the port you want to expose (default: 3000): ").strip() or "3000"
set_env_variable("./src/.env", "PORT", port)
set_env_variable("./src/.env", "HOST", "0.0.0.0")

print("\n🎉 Setup complete!")
print("🚀 Run the following command to start the server:")
print("\tpython src/main.py")
