@echo off
REM  • new-tab: Runs cmd.exe with our cloudflared loop.
REM  • ; split-pane: Splits horizontally (-V) running cmd.exe with our Python loop.
REM Note: Commands are separated by a semicolon.
copy config.yml C:\Users\aranr\.cloudflared\config.yml
wt new-tab -p "Command Prompt" cmd.exe /k "cloudflared tunnel run" ; split-pane -V -p "Command Prompt" cmd.exe /k "cd Desktop && wsl ./start_in_wsl.sh"