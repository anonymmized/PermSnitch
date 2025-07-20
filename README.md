# PermSnitch 🌟🔒
 
![PermSnitch Logo](./logo.png)

**Tags:**  
`Python` 🌱 | [![Python Version](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/) |  
`Cybersecurity` 🔒 | [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE) |  
`Open Source` 🌍 | [![GitHub Stars](https://img.shields.io/github/stars/[your_username]/PermSnitch?style=social)](https://github.com/[your_username]/PermSnitch/stargazers) |  
`Active` 🚀

*A sleek Python tool to scan file permissions and secure your system!*

---

## ✨ Welcome to PermSnitch!  
Hey there! 👋 I’m anonymmized
, a Python enthusiast obsessed with cybersecurity. I created **PermSnitch** to help developers and sysadmins detect risky file permissions and protect their systems. Whether you're securing a server or auditing a codebase, this tool’s got your back! 🚀  

Check it out in action:  

---

## 🌐 Why PermSnitch?  
- **Spot Vulnerabilities**: Identifies files with unsafe permissions (e.g., `777`).
- **Count Files**: Tracks `.conf` and `.log` files with ease.
- **Rich Output**: Beautiful, colorful terminal display powered by the `rich` library.
- **Cross-Platform**: Works on Linux, macOS, and Windows!
- **Open Source**: Free to use, fork, and enhance!  

---

## 🚀 Quick Start  

### Prerequisites  
- Python 3.6+
- `pip` (for installing dependencies)

### Installation  
1. Clone the repo:  
   ```bash
   git clone https://github.com/anonymmized/PermSnitch.git
   cd PermSnitch
   ```
2. Install the dependency:
    ```bash
    pip3 install --user rich
    ```
3. Make the script executable (optional):
    ```bash
    chmod +x run.sh
    ```
### Usage
Run PermSnitch with the provided run.sh script:
    ```bash
    ./run.sh . -r -v --conf --logs
    ```
- -r: Recursive scan
- -v: Verbose output
- --conf: Count .conf files
- --logs: Count .log files
#### Example Output:
```
Directory scanning: .
Found a file with unsafe permissions: ./access.log (777)
Final report:
- Found 1 unsafe files
- Number of .conf files: 1
- Number of .log files: 1
```
#### Save reports:
    ```bash 
    ./run.sh /home -r --csv report.csv --json report.json
    ```

⭐ **Star this repo if you find it useful!**