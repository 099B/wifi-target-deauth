# 📡 Wi-Fi Client Discovery & Targeted Deauthentication Auditor

```text
======================================================
#                 _ _ _ _                            #
#                / \ \ \ \                           #
#               |  | | | |                           #
#            _  |  |_|_|_|                           #
#           / \ |  | | | |                           #
#          |   \|  | | | |                           #
#          |    |  |_|_|_|                           #
#          |    |  | | | |                           #
#          |    \  /_/_/_/                           #
#           \    `-.  /                              #
#            \      _/                               #
#             |    |                                 #
======================================================
```

An interactive Python automation script built on top of the **Aircrack-ng** suite. This tool streamlines Wi-Fi reconnaissance and targeted IEEE 802.11 deauthentication testing by actively harvesting associated client stations on a specific access point (AP) and executing controlled deauthentication bursts against selected devices.

---

## ⚠️ Legal & Ethical Disclaimer

> **IMPORTANT**: This tool is designed strictly for **authorized penetration testing**, educational security research, and network administration diagnostics.
> 
> Unauthorized testing against wireless networks or devices without explicit written permission from the owner is illegal under local, federal, and international law. The author and contributors assume **no liability** for any misuse, damage, or legal consequences resulting from this software.

---

## 🎯 Project Goals

- **Automate Wi-Fi Client Enumeration**: Continuously capture and parse traffic logs in real-time to identify devices connected to a target Access Point (BSSID).
- **Target Filtering & Granular Control**: Allow the auditor to review discovered targets, customize attack burst lengths, and exclude specific stations (e.g., administrator devices or critical hosts).
- **Automated Deauth Injection Loop**: Cycle through target queues using `aireplay-ng` while locking `airodump-ng` on the appropriate channel to maintain link persistence.
- **Clean Signal & State Management**: Gracefully handle process interruptions (`SIGINT` / `Ctrl+C`) to clean up temporary scan files and terminate background processes safely.

---

## 📋 Prerequisites & System Requirements

### 1. Operating System
- **Linux** with wireless monitor mode and raw frame injection support (e.g., **Kali Linux**, **Parrot Security OS**, or Debian/Ubuntu).
- *Note:* macOS and native Windows internal wireless chipsets generally do not support monitor mode or packet injection. Use Linux natively or via a virtual machine with a pass-through USB Wi-Fi adapter.

### 2. Hardware
- A Wi-Fi adapter that supports **Monitor Mode** and **Packet Injection** (e.g., adapters with Atheros AR9271, MediaTek MT7612U / RT3070, or Realtek RTL8812AU chipsets).

### 3. Software Dependencies
Ensure Python 3 and the wireless tools are installed:

```bash
# Update repository lists
sudo apt update

# Install Aircrack-ng suite and iw tools
sudo apt install -y python3 aircrack-ng iw
```

Verify the tools are accessible in your `$PATH`:
```bash
which airodump-ng aireplay-ng iw
```

---

## 🛠️ Pre-Flight Setup (Monitor Mode)

Before running the script, put your wireless interface into monitor mode.

### Method A: Using `airmon-ng` (Recommended)
```bash
# 1. Kill interfering processes (e.g., NetworkManager, wpa_supplicant)
sudo airmon-ng check kill

# 2. Enable monitor mode on your wireless interface (e.g., wlan0)
sudo airmon-ng start wlan0

# 3. Verify interface name (usually becomes wlan0mon)
ip link show
```

### Method B: Using `iw`
```bash
sudo ip link set wlan0 down
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up
```

*(Optional)* Identify target AP details (BSSID and Channel) using:
```bash
sudo airodump-ng wlan0mon
```
*(Press `Ctrl+C` once you identify your target router's MAC and operating channel).*

---

## 🚀 How to Run the Script

Run the script with superuser (`sudo`) privileges:

```bash
sudo python3 wifi-target-deauth.py
```

### Step-by-Step Workflow

#### 1. Interactive Initialization
The script prompts for three required parameters:
- **Monitor mode interface**: e.g., `wlan0mon`
- **Target Router MAC (BSSID)**: e.g., `AA:BB:CC:DD:EE:FF`
- **Operating Channel**: e.g., `1`, `6`, `11`, or `36`

#### 2. Phase 1: Client Harvesting Engine
- The script tunes the wireless interface to the target channel and runs `airodump-ng` in the background.
- It scans real-time CSV traffic and logs connected client stations.
- A live counter displays discovered devices:
  ```text
  [*] Time: 14s | Devices Discovered: [3] | Press Ctrl+C to lock targets
  ```
- Once you are satisfied with the discovered targets, press **`Ctrl+C`** to lock the target list.

#### 3. Target Filter & Approval Gate
- Displays all discovered client MAC addresses.
- Prompts for **burst duration** in seconds (default: `5` seconds).
- Prompts for targets to **skip/exclude** (e.g., type `2` or `1,3`, or press `[ENTER]` to target all).

#### 4. Phase 2: Injection Matrix
- Continuously cycles through the approved target queue.
- Sends 60 deauthentication packets per target burst using `aireplay-ng`.
- Press **`Ctrl+C`** at any point to exit cleanly and release child processes.

---

## 🗂️ Project Structure

```text
.
├── wifi-target-deauth.py  # Main interactive Wi-Fi discovery & deauth audit script
├── .gitignore             # Git exclusion rules for temp files & dumps
└── README.md              # Documentation and operational manual
```

---

## 🔧 Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `[-] Error: This script must be run with 'sudo'` | Not run as superuser | Execute with `sudo python3 wifi-target-deauth.py` |
| `No client devices found connected...` | Short scan window or low traffic | Let Phase 1 scan longer or generate client traffic |
| `Channel -1 / fixed channel error` | Driver or regulatory domain mismatch | Use `--ignore-negative-one` (already built into script) or lock channel with `iw` |
| `Interface busy / operation not permitted` | Background services interfering | Run `sudo airmon-ng check kill` before testing |

---
 

