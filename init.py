import os
import subprocess
import platform
import time
import sys
import shutil

"""Ensures all Python dependencies are installed."""
print("📦 Checking and installing Python dependencies...")

def check_pip():
    """Ensures pip is installed and available."""
    if not shutil.which("pip"):
        print("⚠️ Pip is not installed or not found in PATH. Attempting to install it...")
        subprocess.run([sys.executable, "-m", "ensurepip"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)

def install_dependencies():
    """Installs dependencies from requirements.txt"""
    timeout = 10
    cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Capture output with timeout
        start_time = time.time()
        while time.time() - start_time < timeout:
            output = process.stdout.readline().strip()
            if output:
                if "satisfied" not in output:
                    print(output)
            if process.poll() is not None:
                break

        stdout, stderr = process.communicate(timeout=timeout)
        if process.returncode == 0:
            print("✅ Python dependencies installed successfully.")
        else:
            raise Exception(f"⚠️ Failed to install dependencies.\n{stderr}")
 
    except Exception as e:
        print("⚠️ Failed to install dependencies. Please check your Python & Pip installation.")
        print(f"❌ Error: {e}")
        sys.exit(1)
        
check_pip()
install_dependencies()

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
        set_env_variable("./src/.env", "SHELL", git_bash_path)
    else:
        print("⚠️ Git Bash setup failed. Defaulting to PowerShell.")
        set_env_variable("./src/.env", "SHELL", "powershell.exe")

# 🍏 Mac & 🐧 Linux: Use /bin/bash
elif SYSTEM in ["Darwin", "Linux"]:
    set_env_variable("./src/.env", "SHELL", "/bin/bash")
    
# 🌍 Install playwright 
os.system(f"{sys.executable} -m playwright install")

# 🏠 Setup Port
port = input("Enter the port you want to expose (default: 3000): ").strip() or "3000"
set_env_variable("./src/.env", "PORT", port)
set_env_variable("./src/.env", "HOST", "0.0.0.0")

os.system(f'echo {sys.executable} src/main.py > start_server.bat')
os.system(f'echo {sys.executable} src/main.py > start_server.sh')


print("\n🎉 Setup complete!")
print("🚀 Run the either start_server.bat or start_server.sh to start the server:")

