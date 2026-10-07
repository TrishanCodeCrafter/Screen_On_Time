import json
import os
import time
import datetime

import win32api

import display_utils
from time_tracker import TimeTracker
from power_listener import PowerEventListener


# The inside of the dashboard is 64 terminal columns wide.
# The left and right borders add two more columns.
DASHBOARD_WIDTH = 64


# Some emojis take up two terminal columns even though Python counts
# them as a single character.
#
# This is enough for the emojis currently used by this app.
WIDE_TERMINAL_CHARACTERS = {
    "🔋",
    "🔌",
    "🚀",
    "🖥",
    "💤",
    "⚡",
    "♻",
}


# Python's string formatting counts Unicode characters, but terminals
# care about how many visual columns those characters actually occupy.
#
# Some emojis take up two columns in Windows Terminal, so we account
# for those here when calculating dashboard spacing.
def terminal_text_width(text):
    width = 0

    for char in text:
        if char in WIDE_TERMINAL_CHARACTERS:
            width += 2
        elif char == "\ufe0f":
            # Variation selectors don't take up their own terminal column.
            continue
        else:
            width += 1

    return width


# Add the correct amount of padding so the dashboard borders always
# line up, even when the text contains wide emojis.
def dashboard_line(text=""):
    text_width = terminal_text_width(text)
    padding = DASHBOARD_WIDTH - text_width

    return f"│{text}" + (" " * padding) + "│"


# When booting up for the first time, we need to find the internal display prefix.
# This is basically the monitor ID that identifies the laptop's built-in display.
def save_internal_display(primary_prefix, path="config.json"):
    with open(path, "w") as f:
        json.dump({"internal_display_prefix": primary_prefix}, f)


# If we have a stored config with the primary display prefix, load it.
def load_internal_display(path="config.json"):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f).get("internal_display_prefix")

    return None


# Add a meaningful event to the terminal history.
# We don't want to log every second because the live dashboard already
# shows the current state. The event log is for things worth remembering.
def add_event(event_log, message, emoji="•", max_events=7):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    event_log.append(f"{timestamp}   {emoji}  {message}")

    # Keep the event log small so the dashboard stays the same size.
    if len(event_log) > max_events:
        event_log.pop(0)


# Draw the live terminal dashboard.
#
# Instead of printing a new line every second, we move the terminal cursor
# back to the top and redraw the dashboard in the same place.
def render_dashboard(
    tracker,
    current_battery_level,
    session_battery_level,
    battery_used,
    sot_estimate,
    remaining_time,
    event_log,
    status,
):
    # Move cursor back to the top-left corner of the terminal.
    print("\033[H", end="")

    now = datetime.datetime.now().strftime("%H:%M:%S")
    screen_time = tracker.get_total_time(formatting=True)

    print("╭────────────────────────────────────────────────────────────────╮")

    # The header has the title on the left and current time on the right.
    header = f" 🔋 SOT Tracker"

    header_padding = (
        DASHBOARD_WIDTH
        - terminal_text_width(header)
        - terminal_text_width(now)
        - 1
    )

    print(
        f"│{header}"
        + (" " * header_padding)
        + f"{now} │"
    )

    print("├────────────────────────────────────────────────────────────────┤")
    print(dashboard_line())
    print(
        dashboard_line(
            f"  Screen time      {screen_time:<18}"
            f"Battery          {current_battery_level:>3}%"
        )
    )

    print(
        dashboard_line(
            f"  Battery used     {str(battery_used) + '%':<18}"
            f"Unplugged at     {session_battery_level:>3}%"
        )
    )

    print(dashboard_line())

    print(
        dashboard_line(
            f"  SOT estimate     {str(sot_estimate):<18}"
            f"Remaining      {str(remaining_time):<12}"
        )
    )

    print(dashboard_line())
    print("├────────────────────────────────────────────────────────────────┤")
    print(dashboard_line(" EVENT LOG"))
    print(dashboard_line())

    # Print the most recent events.
    for event in event_log:
        print(dashboard_line(f"  {event}"))

    # Fill unused event rows so the dashboard doesn't change height.
    for _ in range(7 - len(event_log)):
        print(dashboard_line())

    print("├────────────────────────────────────────────────────────────────┤")
    print(dashboard_line(f" {status}"))
    print("╰────────────────────────────────────────────────────────────────╯")

    # Make sure the output appears immediately instead of waiting
    # for Python's normal stdout buffering.
    print("", flush=True)


def main():

    # Check if we have a stored internal display prefix (basically monitor ID).
    primary_prefix = load_internal_display()

    # If not, find it and save it for future use.
    if not primary_prefix:
        primary_prefix = display_utils.find_internal_monitor_id()
        save_internal_display(primary_prefix)

    # Initialize the time tracker and other variables.
    tracker = TimeTracker()

    # Used to detect changes between plugged-in and battery power.
    previous_power_state = None

    # Assume the screen is on initially.
    # This is also used as a flag to avoid starting/stopping the tracker twice.
    listener_screen_on = True

    # Battery level when the current battery session started.
    session_battery_level = win32api.GetSystemPowerStatus()["BatteryLifePercent"]

    sot_estimate = "N/A"
    remaining_time = "N/A"

    # State saved immediately before suspend.
    # We use this after resume to figure out what happened while
    # the computer was asleep.
    suspend_power_state = None
    suspend_battery_level = None

    # The event log is intentionally separate from the live dashboard.
    # The dashboard shows what is happening right now.
    # The event log shows what happened earlier.
    event_log = []

    # -------------------------------------------------------
    # TERMINAL SETUP
    # -------------------------------------------------------

    # Clear the terminal once when the application starts.
    # After this, render_dashboard() will only move the cursor
    # back to the top and redraw the dashboard.
    print("\033[2J\033[H", end="")

    add_event(
        event_log,
        f"Tracker started at {session_battery_level}%",
        "🚀"
    )

    # -------------------------------------------------------
    # POWER / DISPLAY EVENT CALLBACK
    # -------------------------------------------------------

    # Callback function to handle power/display events.
    # Basically, this reacts to screen on/off and system suspend/resume events.
    def listener_callback(display_on, state):

        nonlocal listener_screen_on
        nonlocal suspend_power_state, suspend_battery_level
        nonlocal session_battery_level

        # -------------------------------------------------------
        # SYSTEM SUSPEND
        # -------------------------------------------------------
        if state == "SUSPEND":
            listener_screen_on = False

            # Save state before suspend so we can reconstruct what
            # happened while the process was not running.
            power_status = win32api.GetSystemPowerStatus()
            suspend_power_state = power_status["ACLineStatus"]
            suspend_battery_level = power_status["BatteryLifePercent"]

            add_event(
                event_log,
                f"System suspended at {suspend_battery_level}%",
                "💤"
            )

            if tracker.start_time:
                tracker.stop()

                add_event(
                    event_log,
                    "Tracking paused (system sleep)",
                    "⏸"
                )

        # -------------------------------------------------------
        # SYSTEM RESUME
        # -------------------------------------------------------
        elif state == "RESUME":
            listener_screen_on = True

            power_status = win32api.GetSystemPowerStatus()
            current_power_state = power_status["ACLineStatus"]
            current_battery_level = power_status["BatteryLifePercent"]

            # -------------------------------------------------------
            # Case 1:
            #
            # AC -> Battery while suspended
            #
            # before sleep: AC
            # machine sleeps
            # user unplugs
            # machine wakes: Battery
            # -------------------------------------------------------
            if suspend_power_state == 1 and current_power_state == 0:
                listener_screen_on = True
                tracker.reset()

                # New battery session starts at the current battery level.
                # The main loop will continue the normal tracking logic.
                session_battery_level = current_battery_level

                add_event(
                    event_log,
                    f"Reset session: unplugged during sleep "
                    f"({current_battery_level}%)",
                    "♻️"
                )

            # -------------------------------------------------------
            # Case 2:
            #
            # Battery -> Battery
            #
            # Battery percentage increased while suspended.
            # Therefore, infer that charging happened during suspend.
            # -------------------------------------------------------
            elif (
                suspend_power_state == 0
                and current_power_state == 0
                and suspend_battery_level is not None
                and current_battery_level > suspend_battery_level
            ):
                listener_screen_on = True
                tracker.reset()

                # New battery session starts at the current battery level.
                session_battery_level = current_battery_level

                add_event(
                    event_log,
                    f"Hidden charging detected "
                    f"({suspend_battery_level}% → {current_battery_level}%)",
                    "♻️"
                )

            add_event(
                event_log,
                "System resumed",
                "⚡"
            )

            # Resume normal tracking if we didn't reset/start it above.
            if not tracker.start_time:
                tracker.start()

                add_event(
                    event_log,
                    "Tracking resumed",
                    "▶"
                )

            # IMPORTANT:
            # Do not reuse the old suspend state on a future event.
            suspend_power_state = None
            suspend_battery_level = None

        # -------------------------------------------------------
        # DISPLAY OFF
        # -------------------------------------------------------
        elif state == "OFF":
            listener_screen_on = False

            add_event(
                event_log,
                "Display turned off",
                "🖥️"
            )

            if tracker.start_time:
                tracker.stop()

                add_event(
                    event_log,
                    "Tracking paused",
                    "⏸"
                )

        # -------------------------------------------------------
        # DISPLAY ON
        # -------------------------------------------------------
        elif state == "ON":
            listener_screen_on = True

            add_event(
                event_log,
                "Display turned on",
                "🖥️"
            )

            if not tracker.start_time:
                tracker.start()

                add_event(
                    event_log,
                    "Tracking started",
                    "▶"
                )

    PowerEventListener(callback=listener_callback)

    # -------------------------------------------------------
    # MAIN LOOP
    # -------------------------------------------------------

    try:
        while True:
            time.sleep(1)

            # Get the current power status once per loop.
            # There is no need to call GetSystemPowerStatus() multiple times
            # when all of these values come from the same status snapshot.
            power_status = win32api.GetSystemPowerStatus()

            power_state = 1 if power_status["ACLineStatus"] == 1 else 0
            current_battery_level = power_status["BatteryLifePercent"]

            # Check whether the internal display is currently active.
            display_state = display_utils.is_display_active(primary_prefix)

            # display_state:
            # True = on
            # False = off
            #
            # listener_screen_on:
            # True = screen/system should be tracked
            # False = display was explicitly turned off/suspended
            display_on = display_state and listener_screen_on

            # -------------------------------------------------------
            # DISPLAY / TRACKING STATE
            # -------------------------------------------------------

            if display_on:
                # Display is on and the system is allowed to track.
                if not tracker.start_time:
                    tracker.start()

                    add_event(
                        event_log,
                        "Tracking started",
                        "▶"
                    )

            else:
                if tracker.start_time:
                    tracker.stop()

                    add_event(
                        event_log,
                        "Tracking paused",
                        "⏸"
                    )

            # -------------------------------------------------------
            # POWER STATE CHANGES
            # -------------------------------------------------------

            # Detect transition: Plugged -> Battery.
            if previous_power_state == 1 and power_state == 0:
                tracker.reset()
                tracker.start()

                session_battery_level = current_battery_level

                add_event(
                    event_log,
                    f"Unplugged at {session_battery_level}%",
                    "🔋"
                )

                add_event(
                    event_log,
                    "New battery session",
                    "♻️"
                )

            # Detect transition: Battery -> Plugged.
            if previous_power_state == 0 and power_state == 1:
                add_event(
                    event_log,
                    "Plugged in",
                    "🔌"
                )

                add_event(
                    event_log,
                    "Tracking paused (AC power)",
                    "⏸"
                )

            # Keep track of previous power state for next iteration.
            previous_power_state = power_state

            # -------------------------------------------------------
            # BATTERY / SOT CALCULATIONS
            # -------------------------------------------------------

            # Calculate how much battery has been used during this session.
            battery_used = (
                session_battery_level - current_battery_level
                if power_state == 0
                else "N/A"
            )

            # Calculate SOT estimate only if on battery.
            if power_state == 0:
                sot_estimate, raw_sot_estimate = tracker.sot_estimate(
                    current_battery_level,
                    session_battery_level
                )

            # Calculate remaining time only if SOT estimate is valid.
            if sot_estimate not in ("N/A", "Calculating..."):
                remaining_time = tracker.time_formatting(
                    raw_sot_estimate * (current_battery_level / 100)
                )

            # -------------------------------------------------------
            # TERMINAL DASHBOARD
            # -------------------------------------------------------

            if power_state == 0 and display_on:
                status = "● ON BATTERY   • Ctrl+C to stop"

            elif power_state == 1:
                status = "🔌 PLUGGED IN   • Tracking paused"

            elif not display_on:
                status = "○ DISPLAY OFF   • Tracking paused"

            else:
                status = "◐ PAUSED   • Ctrl+C to stop"

            render_dashboard(
                tracker,
                current_battery_level,
                session_battery_level,
                battery_used,
                sot_estimate,
                remaining_time,
                event_log,
                status,
            )

    except KeyboardInterrupt:
        # Leave the user with a simple final message after Ctrl+C.
        print("\n")
        print(
            f"Exiting... Final screen time: "
            f"{tracker.get_total_time(formatting=True)}"
        )


if __name__ == "__main__":
    main()
