import ctypes
from ctypes import wintypes

# As the name of the file says this gives the primary display name
# This is useful for getting the primary display name in a Windows environment

# Constants
DISPLAY_DEVICE_ACTIVE = 0x00000001
DISPLAY_DEVICE_PRIMARY_DEVICE = 0x00000004

# Structures
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

def primaryDisplay():
    i = 0
    while True:
        device = DISPLAY_DEVICE()
        device.cb = ctypes.sizeof(DISPLAY_DEVICE)
        success = EnumDisplayDevices(None, i, ctypes.byref(device), 0)
        if not success:
            break

        print(f"Device {i}: {device.DeviceString}")
        print(f"  Name: {device.DeviceName}")
        print(f"  Active: {bool(device.StateFlags & DISPLAY_DEVICE_ACTIVE)}")
        print(f"  DIS: {DISPLAY_DEVICE_ACTIVE}")
        print(f"  DIS_PRI: {DISPLAY_DEVICE_PRIMARY_DEVICE}")
        print(f"  Primary: {bool(device.StateFlags & DISPLAY_DEVICE_PRIMARY_DEVICE)}")
        print(f"  DeviceID: {device.DeviceID}")
        print(f"  StateFlags: {device.StateFlags}")
        print(f"  Key: {device.DeviceKey}\n")
        
        if device.StateFlags & DISPLAY_DEVICE_PRIMARY_DEVICE and device.StateFlags & DISPLAY_DEVICE_ACTIVE:
            print(f"Primary display found: {device.DeviceName}")
            return device.DeviceName
        

        i += 1


primaryDisplay()