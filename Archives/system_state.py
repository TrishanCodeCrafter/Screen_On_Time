# system_state.py
import win32api

def on_display_change(display_active):
    """
    Unified handler for display/power state.
    
    display_active: result from display_utils.is_display_active(prefix) (True/False)
    """

    # Default assumption: AC power unless event says otherwise
    power_state = 1 if win32api.GetSystemPowerStatus()['ACLineStatus'] == 1 else 0

    if power_state:
        display_on, state = power_event
        display_state = display_on
        power_state = 1 if power_state else 0
    else:
        display_state = display_active

    return display_state, power_state
