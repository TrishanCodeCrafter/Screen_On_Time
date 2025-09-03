import win32con
import win32gui
import win32api
import win32gui_struct
import win32process
import ctypes
import uuid
import time
import threading

import Screen_On_Time.Archives.core as core


GUID_CONSOLE_DISPLAY_STATE = uuid.UUID('{6FE69556-704A-47A0-8F24-C28D936FDA47}')
PBT_POWERSETTINGCHANGE = 0x8013
WM_POWERBROADCAST = 0x0218
start_time = time.time()

class PowerEventListener:
    def __init__(self):
        self.display_on = True  # Assume it's on initially
        self.running = True
        
        # Create and run a window in a thread
        self.thread = threading.Thread(target=self._create_message_window, daemon=True)
        self.thread.start()


    def _register_power_setting_notification(self, hwnd):
        GUID_CONSOLE_DISPLAY_STATE = ctypes.c_byte * 16
        guid = GUID_CONSOLE_DISPLAY_STATE.from_buffer_copy(
            uuid.UUID('{6FE69556-704A-47A0-8F24-C28D936FDA47}').bytes_le
        )

        device_notify_window_handle = 0x00000000
        ctypes.windll.user32.RegisterPowerSettingNotification(
            hwnd,
            ctypes.byref(guid),
            device_notify_window_handle
        )

    
    def _create_message_window(self):
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "PowerEventWindow"
        wc.lpfnWndProc = self._wnd_proc  # Callback
        class_atom = win32gui.RegisterClass(wc)
        hwnd = win32gui.CreateWindow(wc.lpszClassName,
                                     "PowerEventWindow",
                                     0,
                                     0, 0, 0, 0,
                                     0, 0, hinst, None)
        self._register_power_setting_notification(hwnd)
        win32gui.PumpMessages()


    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        
            print()
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

                print(f"Power setting changed: {guid} - {data}")
                if guid == GUID_CONSOLE_DISPLAY_STATE:
                    if data == 0:
                        print("🔴 Display OFF")
                        elapsed_time = time.time() - start_time
                        print(f"Screen ON Time: {elapsed_time//60} minutes {elapsed_time%60} seconds")
                        self.display_on = False
                    elif data == 1:
                        print("🟢 Display ON")
                        self.display_on = True
                    elif data == 2:
                        print("🟡 Display DIMMED")
            return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)


if __name__ == "__main__":
    listener = PowerEventListener()
    print("Listener started. Press Ctrl+C to exit.")

    try:
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        print("Exiting...")


if listener.display_on:
    elapsed_time = time.time() - start_time
    print(f"Screen ON Time: {elapsed_time:.2f} seconds")

