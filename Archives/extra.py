import ctypes
from ctypes import wintypes

# Constants
DISPLAY_DEVICE_ACTIVE = 0x00000001
DISPLAY_DEVICE_PRIMARY_DEVICE = 0x00000004

class DISPLAY_DEVICE(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("DeviceName", wintypes.WCHAR * 32),
        ("DeviceString", wintypes.WCHAR * 128),
        ("StateFlags", wintypes.DWORD),
        ("DeviceID", wintypes.WCHAR * 128),
        ("DeviceKey", wintypes.WCHAR * 128)
    ]

EnumDisplayDevices = ctypes.windll.user32.EnumDisplayDevicesW
print("Hey there!",EnumDisplayDevices)

def list_displays():
    i = 0
    while True:
        adapter = DISPLAY_DEVICE()
        adapter.cb = ctypes.sizeof(DISPLAY_DEVICE)
        if not EnumDisplayDevices(None, i, ctypes.byref(adapter), 0):
            break

        print(f"Adapter {i}: {adapter.DeviceString}")
        print(f"  Name: {adapter.DeviceName}")
        print(f"  DeviceID (GPU): {adapter.DeviceID}")
        print(f"  Primary: {bool(adapter.StateFlags & DISPLAY_DEVICE_PRIMARY_DEVICE)}")
        print(f"  Active: {bool(adapter.StateFlags & DISPLAY_DEVICE_ACTIVE)}\n")

        # Now enumerate monitors attached to this adapter
        j = 0
        while True:
            monitor = DISPLAY_DEVICE()
            monitor.cb = ctypes.sizeof(DISPLAY_DEVICE)
            if not EnumDisplayDevices(adapter.DeviceName, j, ctypes.byref(monitor), 0):
                break

            print(f"    Monitor {j}: {monitor.DeviceString}")
            print(f"      Name: {monitor.DeviceName}")
            print(f"      DeviceID (Monitor): {monitor.DeviceID}")
            print(f"      Active: {bool(monitor.StateFlags & DISPLAY_DEVICE_ACTIVE)}\n")
            j += 1

        i += 1

if __name__ == "__main__":
    list_displays()






























# import time
# import display_utils
# from power_listener import PowerEventListener

# start_time = time.time()


# def on_display_change(display_on, state):
#     if state == "OFF":
#         elapsed = time.time() - start_time
#         print(f"🔴 Display OFF — Screen ON Time: {elapsed:.2f} sec")
#     elif state == "ON":
#         print("🟢 Display ON")
#     elif state == "DIMMED":
#         print("🟡 Display DIMMED")

# if __name__ == "__main__":
#     primary = display_utils.primary_display_name()
#     print(f"Primary display: {primary}")
    

#     if display_utils.is_display_active(primary):
#         print("Primary display is ACTIVE")
#     else:
#         print("Primary display is INACTIVE")

#     listener = PowerEventListener(callback=on_display_change)
#     print("Listening for power/display events... Press Ctrl+C to stop.")
#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("Exiting...")

