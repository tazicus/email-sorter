# Setup Instructions

## 1. Install Python

1. Go to https://www.python.org/downloads/ and download the latest Python 3.x installer
2. Run the installer — **check "Add python.exe to PATH"** before clicking Install
3. Restart your editor (VS Code / IDE) so it picks up the new PATH

## 2. Create virtual environment and install dependencies

Open a terminal in the project folder and run:

```powershell
cd "g:\My Drive\Claud_Code_project_1"
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. Fix Account 2 in .env

Before testing, make sure Account 2 has both fields correct:

```
EMAIL_ADDRESS_2=you@yourdomain.com
EMAIL_PASSWORD_2=your-password-here
```

Currently `EMAIL_ADDRESS_2` appears to contain a password value and `EMAIL_PASSWORD_2` is missing.

## 4. Test IMAP connections

```powershell
python test_connections.py
```

This will connect to each account and report how many unread emails are in the inbox — without moving anything.
