import win32con
import win32gui
import win32api
import ctypes
import uuid
import threading

PBT_POWERSETTINGCHANGE = 0x8013
WM_POWERBROADCAST = 0x0218

GUID_CONSOLE_DISPLAY_STATE = uuid.UUID('{6FE69556-704A-47A0-8F24-C28D936FDA47}')

class PowerEventListener:
    def __init__(self, callback=None):
        """
        callback: function(display_on: bool, state: str) -> None
        state = 'ON', 'OFF', 'DIMMED'
        """
        self.display_on = True
        self.callback = callback
        self.thread = threading.Thread(target=self._create_message_window, daemon=True)
        self.thread.start()

    def _register_power_setting_notification(self, hwnd):
        GUID_STRUCT = ctypes.c_byte * 16
        guid_bytes = GUID_STRUCT.from_buffer_copy(GUID_CONSOLE_DISPLAY_STATE.bytes_le)
        device_notify_window_handle = 0x00000000
        ctypes.windll.user32.RegisterPowerSettingNotification(
            hwnd,
            ctypes.byref(guid_bytes),
            device_notify_window_handle
        )

    def _create_message_window(self):
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "PowerEventWindow"
        wc.lpfnWndProc = self._wnd_proc
        win32gui.RegisterClass(wc)
        hwnd = win32gui.CreateWindow(
            wc.lpszClassName, "PowerEventWindow",
            0, 0, 0, 0, 0, 0, 0, hinst, None
        )
        self._register_power_setting_notification(hwnd)
        win32gui.PumpMessages()

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == WM_POWERBROADCAST and wparam == PBT_POWERSETTINGCHANGE:
            class GUID(ctypes.Structure):
                _fields_ = [
                    ("Data1", ctypes.c_uint32),
                    ("Data2", ctypes.c_uint16),
                    ("Data3", ctypes.c_uint16),
                    ("Data4", ctypes.c_ubyte * 8)
                ]
            class POWERBROADCAST_SETTING(ctypes.Structure):
                _fields_ = [
                    ("PowerSetting", GUID),
                    ("DataLength", ctypes.c_ulong),
                    ("Data", ctypes.c_ubyte * 1)
                ]
            setting = ctypes.cast(lparam, ctypes.POINTER(POWERBROADCAST_SETTING)).contents
            raw_guid_bytes = bytes(ctypes.string_at(ctypes.byref(setting.PowerSetting), ctypes.sizeof(GUID)))
            guid = uuid.UUID(bytes_le=raw_guid_bytes)
            data = setting.Data[0]

            if guid == GUID_CONSOLE_DISPLAY_STATE:
                if data == 0:
                    self.display_on = False
                    if self.callback:
                        self.callback(False, "OFF")
                elif data == 1:
                    self.display_on = True
                    if self.callback:
                        self.callback(True, "ON")
                elif data == 2:
                    if self.callback:
                        self.callback(True, "DIMMED")
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
