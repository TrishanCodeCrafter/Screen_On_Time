import json
import os
import time
import win32api
import display_utils
#from Archives.power_listener import PowerEventListener

start_time = time.time()


def on_display_change(is_active):#display_on, state, primary_prefix):
    
    # is_active checks if the stored internal display is currently active
    #is_active = display_utils.is_display_active(primary_prefix)
    
    #debug print
    #print(display_on, state, primary_prefix, is_active)
    
    # if state == "ON" and is_active:
    #     print("🟢 Display ON")
    # elif state == "DIMMED" and is_active:
    #     print("🟡 Display DIMMED")
    # else:
    #     print(f"🔴 Display OFF")
    
    
    
    if is_active:
        
        # Check power status
        status = win32api.GetSystemPowerStatus()
        
        print(f"🟢 Display ON | Time: {int(time.time() - start_time)} sec | Power Status:", "AC 🔌" if status['ACLineStatus'] == 1 else "Battery 🔋")
        
        
    else:
        print(f"🔴 Display OFF")
    
    # if state == "OFF" and is_active:
    #     elapsed = time.time() - start_time
    #     print(f"🔴 Display OFF — Screen ON Time: {elapsed:.2f} sec")
    # elif state == "ON" and is_active:
    #     print("🟢 Display ON")
    # elif state == "DIMMED" and is_active:
    #     print("🟡 Display DIMMED")

def save_internal_display(primary_prefix, path="config.json"):
    with open(path, "w") as f:
        json.dump({"internal_display_prefix": primary_prefix}, f)

def load_internal_display(path="config.json"):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f).get("internal_display_prefix")
    return None

def main():
    
    # Check if we have a stored internal display prefix
    primary_prefix = load_internal_display()
    
    if not primary_prefix:
        
        primary_prefix, display_name = display_utils.find_internal_monitor_id()
        save_internal_display(primary_prefix)   
         
    #listener = PowerEventListener(callback=on_display_change)
    #listener = PowerEventListener(callback=lambda display_on, state: on_display_change(display_on, state, primary_prefix))

    #listener = PowerEventListener(callback=lambda display_on, state, on_ac: on_display_change(display_on, state, primary_prefix))   

    print("Listening for power/display events... Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
            
            
            on_display_change(display_utils.is_display_active(primary_prefix))
            
            
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()
