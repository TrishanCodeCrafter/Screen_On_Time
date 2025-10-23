import json
import os
import time
import win32api
import display_utils
from time_tracker import TimeTracker
from power_listener import PowerEventListener


# When booting up for the first time, we need to find the internal display prefix
def save_internal_display(primary_prefix, path="config.json"):
    with open(path, "w") as f:
        json.dump({"internal_display_prefix": primary_prefix}, f)

# If we have a stored config with primary display prefix, load it
def load_internal_display(path="config.json"):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f).get("internal_display_prefix")
    return None

def main():
    
    # Check if we have a stored internal display prefix (basically monitor ID)
    primary_prefix = load_internal_display()
    
    # If not, find it and save it for future use
    if not primary_prefix:
        
        primary_prefix = display_utils.find_internal_monitor_id()
        save_internal_display(primary_prefix)   
         
  
    # Initialize the time tracker and other variables
    tracker = TimeTracker()
    previous_power_state = None
    listener_screen_on = True # Assume screen is on initially and this is like a flag to avoid double start
    session_battery_level = win32api.GetSystemPowerStatus()['BatteryLifePercent'] # To store the battery level at the start of the session
    SOT_Estimate = "N/A" # Initial SOT estimate

    # Callback function to handle power/display events, basically screen on/off
    def listener_callback(display_on, state):
        
        nonlocal listener_screen_on # To modify the outer variable
        
        print("⚡ Power event:", display_on, state)

        # Pretty self-explanatory cases
        if state == "SUSPEND":
            listener_screen_on = False
            if tracker.start_time:
                tracker.stop()
                print("💤 Tracking paused (system sleep).")

        elif state == "RESUME":
            listener_screen_on = True
            if not tracker.start_time:
                tracker.start()
                print("🔋 Tracking resumed (system wake).")

        elif state == "OFF":
            listener_screen_on = False
            if tracker.start_time:
                tracker.stop()
                print("⏸ Tracking paused (display off).")

        elif state == "ON":
            listener_screen_on = True
            if not tracker.start_time:
                tracker.start()
                print("🔋 Tracking started (display on).")
                
    PowerEventListener(callback=listener_callback)

    print("Listening for power/display events... Press Ctrl+C to stop.")
    
    
    # Now this is the main loop that checks the display and power state every second, 
    # here display state includes projection state too
    try:
        while True:
            time.sleep(1)
            
            # Check display state and power state every second
            display_state = display_utils.is_display_active(primary_prefix)
            power_state = 1 if win32api.GetSystemPowerStatus()['ACLineStatus'] == 1 else 0
            
            # display state: True = on, False = off , this handles the display changes happening through projeciton mode changes
            # power state: 0 = Battery, 1 = AC/Plugged
            
            
            if display_state and listener_screen_on:  # Screen is on according to both methods
                # display on
                if not tracker.start_time:  
                    tracker.start()
                    print("🔋 Tracking started (on battery).")
                    
            else:
                if tracker.start_time:
                    tracker.stop()
                    print("⏸ Tracking paused (plugged in or display off).")

            # Detect transition: Plugged → Battery
            if previous_power_state == 1 and power_state == 0:
                tracker.reset()
                tracker.start()
                session_battery_level = win32api.GetSystemPowerStatus()['BatteryLifePercent'] # Reset session battery level
                print("♻️ Reset tracker (switched to battery).")

            # Keep track of previous power state for next iteration
            previous_power_state = power_state

            # Get current battery level
            current_battery_level = win32api.GetSystemPowerStatus()['BatteryLifePercent']

            # For display purposes                    
            battery_used = session_battery_level - current_battery_level if session_battery_level >= current_battery_level else 0

            # Calculate SOT estimate only if on battery
            if power_state == 0:
                SOT_Estimate = tracker.sot_estimate(current_battery_level, session_battery_level)
              
            

            print(f"⏱ Total time so far: {tracker.get_total_time(formatting=True)} for {battery_used}% drop | 🔋 Session battery level: {session_battery_level}% | SOT Estimate: {SOT_Estimate}")
        

    except KeyboardInterrupt:
        print(f"Exiting... Final screen time: {tracker.get_total_time(formatting=True)} seconds")

if __name__ == "__main__":
    main()
