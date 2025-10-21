
import subprocess
import time
import os

PING_TARGET = "192.168.1.1"
CHECK_INTERVAL = 30
FAIL_THRESHOLD = 4
WIFI_INTERFACE = "wlan0"

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

def has_network():
    try:
        subprocess.check_output(
            ["ping", "-c", "1", "-W", "3", PING_TARGET],
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False

def restart_wifi():
    log("Attempting to restart Wi-Fi...")
    try:
        subprocess.run(
            ["sudo", "ifconfig", WIFI_INTERFACE, "down"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(5)
        subprocess.run(
            ["sudo", "ifconfig", WIFI_INTERFACE, "up"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(20)
        log("Wi-Fi restart complete.")
    except subprocess.CalledProcessError as e:
        log(f"Error restarting Wi-Fi: {e}")

def main():
    failures = 0
    while True:
        if has_network():
            failures = 0
        else:
            failures += 1
            log(f"No connection to {PING_TARGET} ({failures}/{FAIL_THRESHOLD})")
            if failures >= FAIL_THRESHOLD:
                log("No network for 2 minutes. Restarting Wi-Fi...")
                restart_wifi()
                if not has_network():
                    log("Still no network after Wi-Fi restart. Rebooting...")
                    os.system("sudo reboot")
                failures = 0
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    log("Wi-Fi Watchdog started.")
    main()
