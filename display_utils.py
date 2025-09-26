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

def find_internal_monitor_id():
    """Return the name of the primary display device."""
    i = 0
    while True:
        adapter = DISPLAY_DEVICE()
        adapter.cb = ctypes.sizeof(adapter)
        if not EnumDisplayDevices(None, i, ctypes.byref(adapter), 0):
            break
        j = 0
        while True:
            mon = DISPLAY_DEVICE()
            mon.cb = ctypes.sizeof(mon)
            if not EnumDisplayDevices(adapter.DeviceName, j, ctypes.byref(mon), 0):
                break
            
            if adapter.StateFlags & DISPLAY_DEVICE_PRIMARY_DEVICE:
                prefix = mon.DeviceID.split("\\{")[0]  # e.g. 'MONITOR\SDC416E'
            return prefix, mon.DeviceName
            j += 1
        i += 1
    return None, None

def is_display_active(stored_prefix):
    """Check if the given display device is active."""
    i = 0
    while True:
        adapter = DISPLAY_DEVICE()
        adapter.cb = ctypes.sizeof(adapter)
        if not EnumDisplayDevices(None, i, ctypes.byref(adapter), 0):
            break
        j = 0
        while True:
            mon = DISPLAY_DEVICE()
            mon.cb = ctypes.sizeof(mon)
            if not EnumDisplayDevices(adapter.DeviceName, j, ctypes.byref(mon), 0):
                break
            if mon.DeviceID.startswith(stored_prefix):
                return bool(mon.StateFlags & DISPLAY_DEVICE_ACTIVE)
            j += 1
        i += 1
    return False
