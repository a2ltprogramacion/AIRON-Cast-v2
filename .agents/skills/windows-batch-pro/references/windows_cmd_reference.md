# High-Density Windows CMD Reference

A concise dictionary of the most powerful commands for A2LT automation.

## File & Directory Management

| Command    | Purpose         | Essential Flags                  |
| ---------- | --------------- | -------------------------------- |
| `DIR`      | List contents   | `/B` (Bare), `/S` (Recursive)    |
| `DEL`      | Delete file     | `/F` (Force), `/Q` (Quiet)       |
| `MD/RD`    | Make/Remove Dir | `/S` (Recursive for RD)          |
| `XCOPY`    | Copy files/tree | `/E` (Subdirs), `/Y` (Overwrite) |
| `ROBOCOPY` | Robust Copy     | `/MIR` (Mirror), `/Z` (Resume)   |

## System & Process Control

- `TASKLIST`: Displays all running processes.
- `TASKKILL /F /IM "app.exe"`: Forcefully terminates a process.
- `SHUTDOWN /R /T 0`: Immediate reboot.

## Text & Variable Manipulation

- `FINDSTR /R "pattern" file.txt`: Regex search in text.
- `SET /P VAR="Input: "`: Interactive user input.
- `SET /A VAR=1+1`: Arithmetic evaluation.

## Network Commands

- `NETSTAT -AN`: View active connections and ports.
- `IPCONFIG /FLUSHDNS`: Clear DNS cache.
- `PING -N 1 google.com`: Connectivity check (1 packet).
