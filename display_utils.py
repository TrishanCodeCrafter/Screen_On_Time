import ctypes
from ctypes import wintypes

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

class DEVMODE(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", wintypes.WCHAR * 32),
        ("dmSpecVersion", wintypes.WORD),
        ("dmDriverVersion", wintypes.WORD),
        ("dmSize", wintypes.WORD),
        ("dmDriverExtra", wintypes.WORD),
        ("dmFields", wintypes.DWORD),
        ("dmPosition_x", ctypes.c_long),
        ("dmPosition_y", ctypes.c_long),
        ("dmDisplayOrientation", wintypes.DWORD),
        ("dmDisplayFixedOutput", wintypes.DWORD),
        ("dmColor", wintypes.WORD),
        ("dmDuplex", wintypes.WORD),
        ("dmYResolution", wintypes.WORD),
        ("dmTTOption", wintypes.WORD),
        ("dmCollate", wintypes.WORD),
        ("dmFormName", wintypes.WCHAR * 32),
        ("dmLogPixels", wintypes.WORD),
        ("dmBitsPerPel", wintypes.DWORD),
        ("dmPelsWidth", wintypes.DWORD),
        ("dmPelsHeight", wintypes.DWORD),
        ("dmDisplayFlags", wintypes.DWORD),
        ("dmDisplayFrequency", wintypes.DWORD),
        ("dmICMMethod", wintypes.DWORD),
        ("dmICMIntent", wintypes.DWORD),
        ("dmMediaType", wintypes.DWORD),
        ("dmDitherType", wintypes.DWORD),
        ("dmReserved1", wintypes.DWORD),
        ("dmReserved2", wintypes.DWORD),
        ("dmPanningWidth", wintypes.DWORD),
        ("dmPanningHeight", wintypes.DWORD),
    ]

EnumDisplayDevices = ctypes.windll.user32.EnumDisplayDevicesW
EnumDisplaySettings = ctypes.windll.user32.EnumDisplaySettingsW

def primary_display_name():
    """Return the name of the primary display device."""
    i = 0
    while True:
        device = DISPLAY_DEVICE()
        device.cb = ctypes.sizeof(DISPLAY_DEVICE)
        if not EnumDisplayDevices(None, i, ctypes.byref(device), 0):
            break
        
        # print(EnumDisplayDevices(None, i, ctypes.byref(device), 0))
        # print(f"Device {i}: {device.DeviceString}")
        # print(f"  Name: {device.DeviceName}")
        # print(f"  Active: {bool(device.StateFlags & DISPLAY_DEVICE_ACTIVE)}")
        # print(f"  DIS: {DISPLAY_DEVICE_ACTIVE}")
        # print(f"  DIS_PRI: {DISPLAY_DEVICE_PRIMARY_DEVICE}")
        # print(f"  Primary: {bool(device.StateFlags & DISPLAY_DEVICE_PRIMARY_DEVICE)}")
        # print(f"  DeviceID: {device.DeviceID}")
        # print(f"  StateFlags: {device.StateFlags}")
        # print(f"  Key: {device.DeviceKey}\n")
        
        
        if (device.StateFlags & DISPLAY_DEVICE_PRIMARY_DEVICE
                and device.StateFlags & DISPLAY_DEVICE_ACTIVE):
            return device.DeviceName
        i += 1
    return None

def is_display_active(device_name):
    """Check if the given display device is active."""
    devmode = DEVMODE()
    devmode.dmSize = ctypes.sizeof(DEVMODE)
    result = EnumDisplaySettings(device_name, -1, ctypes.byref(devmode))
    return result != 0
