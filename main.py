import json
import os
import time
import display_utils
from power_listener import PowerEventListener

start_time = time.time()


def on_display_change(display_on, state):
    if state == "OFF":
        elapsed = time.time() - start_time
        print(f"🔴 Display OFF — Screen ON Time: {elapsed:.2f} sec")
    elif state == "ON":
        print("🟢 Display ON")
    elif state == "DIMMED":
        print("🟡 Display DIMMED")

def save_internal_display(name, path="config.json"):
    with open(path, "w") as f:
        json.dump({"internal_display": name}, f)

def load_internal_display(path="config.json"):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f).get("internal_display")
    return None

def main():
    # Phase 1: Startup
    primary = load_internal_display()
    if not primary:
        print("No stored display. Capturing primary display...")
        primary = display_utils.primary_display_name()
        save_internal_display(primary)
        print(f"Stored internal display: {primary}")
    else:
        print(f"Loaded stored display: {primary}")

    # Phase 2: Monitor   
    if display_utils.is_display_active(primary):
        print("Primary display is ACTIVE")
    else:
        print("Primary display is INACTIVE")
    
         
    listener = PowerEventListener(callback=on_display_change)
    print("Listening for power/display events... Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()
