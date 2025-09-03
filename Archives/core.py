import ctypes
from ctypes import wintypes
import Screen_On_Time.Archives.Get_primary as Get_primary

# This code checks if the primary display is active using the DEVMODE structure
# and the EnumDisplaySettings function from the Windows API.
# I will use the Get_primary module to get the primary display name

# # Same structures/constants as before
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

EnumDisplaySettings = ctypes.windll.user32.EnumDisplaySettingsW

def is_display_active(device_name):
    devmode = DEVMODE()
    devmode.dmSize = ctypes.sizeof(DEVMODE)
    
    result = EnumDisplaySettings(device_name, -1, ctypes.byref(devmode))
    return result != 0

# Example usage:
if is_display_active(Get_primary.primaryDisplay()):
    print("🟢 Internal display is active")
else:
    print("🔴 Internal display is OFF or not attached")
