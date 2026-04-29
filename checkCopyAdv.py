import ctypes
from ctypes import wintypes
import threading
import time
import logging

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ============================================================
# Windows API Konstanten
# ============================================================

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WH_MOUSE_LL = 14
WH_KEYBOARD_LL = 13
HC_ACTION = 0

WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_MOUSEWHEEL = 0x020A
WM_HOTKEY = 0x0312
WM_KEYDOWN = 0x0100
WM_QUIT = 0x0012

VK_F9 = 0x78
VK_F10 = 0x79

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000

HOTKEY_ID_F9 = 1
HOTKEY_ID_F10 = 2

LLMHF_INJECTED = 0x00000001

INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

# ============================================================
# Windows API Strukturen
# ============================================================

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", POINT),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", wintypes.WPARAM),
    ]

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", wintypes.WPARAM),
    ]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", wintypes.WPARAM),
    ]

class _INPUTUNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]

class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTUNION)]

class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", POINT),
        ("lPrivate", wintypes.DWORD),
    ]

# ============================================================
# API Signaturen und Typisierung
# ============================================================

LowLevelMouseProc = ctypes.WINFUNCTYPE(
    wintypes.LPARAM, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
)
LowLevelKeyboardProc = ctypes.WINFUNCTYPE(
    wintypes.LPARAM, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
)

user32.SetWindowsHookExW.argtypes = (
    ctypes.c_int, ctypes.c_void_p, wintypes.HINSTANCE, wintypes.DWORD
)
user32.SetWindowsHookExW.restype = wintypes.HHOOK

user32.UnhookWindowsHookEx.argtypes = (wintypes.HHOOK,)
user32.UnhookWindowsHookEx.restype = wintypes.BOOL

user32.CallNextHookEx.argtypes = (
    wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
)
user32.CallNextHookEx.restype = wintypes.LPARAM

user32.GetMessageW.argtypes = (
    ctypes.POINTER(MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT
)
user32.GetMessageW.restype = wintypes.BOOL

user32.TranslateMessage.argtypes = (ctypes.POINTER(MSG),)
user32.TranslateMessage.restype = wintypes.BOOL

user32.DispatchMessageW.argtypes = (ctypes.POINTER(MSG),)
user32.DispatchMessageW.restype = wintypes.LPARAM

user32.RegisterHotKey.argtypes = (
    wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT
)
user32.RegisterHotKey.restype = wintypes.BOOL

user32.UnregisterHotKey.argtypes = (wintypes.HWND, ctypes.c_int)
user32.UnregisterHotKey.restype = wintypes.BOOL

user32.GetCursorPos.argtypes = (ctypes.POINTER(POINT),)
user32.GetCursorPos.restype = wintypes.BOOL

user32.SetCursorPos.argtypes = (ctypes.c_int, ctypes.c_int)
user32.SetCursorPos.restype = wintypes.BOOL

user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
user32.SendInput.restype = wintypes.UINT

user32.PostThreadMessageW.argtypes = (
    wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
)
user32.PostThreadMessageW.restype = wintypes.BOOL

kernel32.GetModuleHandleW.argtypes = (wintypes.LPCWSTR,)
kernel32.GetModuleHandleW.restype = wintypes.HMODULE

kernel32.GetCurrentThreadId.argtypes = ()
kernel32.GetCurrentThreadId.restype = wintypes.DWORD

# ============================================================
# Hilfsfunktionen
# ============================================================

def send_mouse_click(x, y):
    """Simuliert einen Mausklick auf Position (x, y)"""
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.01)
    
    down = INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, 0))
    up = INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, 0))
    arr = (INPUT * 2)(down, up)
    user32.SendInput(2, arr, ctypes.sizeof(INPUT))
    
    time.sleep(0.01)

# ============================================================
# Hauptanwendung
# ============================================================

class CheckCopyApp:
    STATE_STOPPED = "STOPPED"
    STATE_RECORDING = "RECORDING"
    STATE_ACTIVE = "ACTIVE"

    def __init__(self):
        self.state = self.STATE_STOPPED
        self.state_lock = threading.Lock()
        
        # Gespeicherte Klick-Positionen
        self.click_pos_x1 = None
        self.click_pos_x2 = None
        
        # Native Hooks
        self.h_mouse = None
        self.h_keyboard = None
        self.thread_id = None
        self._mouse_proc_ref = None
        self._keyboard_proc_ref = None
        
        self.running = True

    def toggle_record(self):
        """F9 - Toggle Recording Mode"""
        with self.state_lock:
            if self.state == self.STATE_STOPPED:
                self.state = self.STATE_RECORDING
                self.click_pos_x1 = None
                self.click_pos_x2 = None
                logging.info(">>> RECORDING MODE: Klicke auf 2 Spalten")
            else:
                self.state = self.STATE_STOPPED
                logging.info(">>> STOPPED")

    def toggle_copy(self):
        """F10 - Toggle Copy Mode"""
        with self.state_lock:
            current = self.state
            
        if current == self.STATE_RECORDING:
            logging.info("Kann nicht in Copy-Mode während Recording wechseln")
            return
            
        if current == self.STATE_STOPPED:
            self.state = self.STATE_ACTIVE
            logging.info(">>> ACTIVE MODE: Klicke zum duplizieren")
        else:
            self.state = self.STATE_STOPPED
            logging.info(">>> STOPPED")

    def handle_mouse_event(self, x, y):
        """Verarbeitet Mausereignisse"""
        with self.state_lock:
            current_state = self.state

        if current_state == self.STATE_RECORDING:
            # X-Positionen speichern
            if self.click_pos_x1 is None:
                self.click_pos_x1 = x
                logging.info(f"X1 gespeichert: {x}")
            elif self.click_pos_x2 is None:
                self.click_pos_x2 = x
                logging.info(f"X2 gespeichert: {x}")
                # Nach 2. Klick: Auto-Stop Recording
                self.state = self.STATE_STOPPED
                logging.info("Recording abgeschlossen. Drücke F10 für Copy-Mode")
            return True  # Event unterdrücken (nicht an System weitergeben)

        elif current_state == self.STATE_ACTIVE:
            # Dupliziere Klicks
            if self.click_pos_x1 is not None and self.click_pos_x2 is not None:
                logging.info(f"Dupliziere Klicks: Y={y}")
                # Klick auf X1, Y
                send_mouse_click(self.click_pos_x1, y)
                time.sleep(0.05)
                # Klick auf X2, Y
                send_mouse_click(self.click_pos_x2, y)
                return True  # Originalklick unterdrücken
            return False

        return False

    def hook_thread(self):
        """Separater Thread für Hooks und Hotkeys"""
        self.thread_id = kernel32.GetCurrentThreadId()
        
        # Erstelle Callback-Funktionen
        self._mouse_proc_ref = LowLevelMouseProc(self._mouse_proc)
        self._keyboard_proc_ref = LowLevelKeyboardProc(self._keyboard_proc)
        
        h_instance = kernel32.GetModuleHandleW(None)
        
        # Installiere Hooks
        self.h_mouse = user32.SetWindowsHookExW(
            WH_MOUSE_LL, self._mouse_proc_ref, h_instance, 0
        )
        if not self.h_mouse:
            logging.error("Mouse-Hook Installation fehlgeschlagen")
            return
        
        self.h_keyboard = user32.SetWindowsHookExW(
            WH_KEYBOARD_LL, self._keyboard_proc_ref, h_instance, 0
        )
        if not self.h_keyboard:
            user32.UnhookWindowsHookEx(self.h_mouse)
            logging.error("Keyboard-Hook Installation fehlgeschlagen")
            return
        
        # Registriere Hotkeys
        ok_f9 = user32.RegisterHotKey(None, HOTKEY_ID_F9, MOD_CONTROL | MOD_ALT | MOD_SHIFT, VK_F9)
        ok_f10 = user32.RegisterHotKey(None, HOTKEY_ID_F10, MOD_CONTROL | MOD_ALT | MOD_SHIFT, VK_F10)
        
        if not ok_f9 or not ok_f10:
            logging.error("Hotkey-Registrierung fehlgeschlagen")
            return
        
        logging.info("Hooks und Hotkeys installiert")
        logging.info("Ctrl+Alt+Shift+F9 = Recording Mode Toggle")
        logging.info("Ctrl+Alt+Shift+F10 = Copy Mode Toggle")
        
        # Message Loop
        msg = MSG()
        while self.running:
            result = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if result == 0 or result == -1:
                break
            
            if msg.message == WM_HOTKEY:
                if msg.wParam == HOTKEY_ID_F9:
                    self.toggle_record()
                elif msg.wParam == HOTKEY_ID_F10:
                    self.toggle_copy()
            
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        
        # Cleanup
        user32.UnregisterHotKey(None, HOTKEY_ID_F9)
        user32.UnregisterHotKey(None, HOTKEY_ID_F10)
        if self.h_keyboard:
            user32.UnhookWindowsHookEx(self.h_keyboard)
        if self.h_mouse:
            user32.UnhookWindowsHookEx(self.h_mouse)

    def _mouse_proc(self, nCode, wParam, lParam):
        try:
            if nCode == HC_ACTION:
                info = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
                x = info.pt.x
                y = info.pt.y
                injected = bool(info.flags & LLMHF_INJECTED)
                
                # Ignoriere unsere eigenen injizierten Klicks
                if injected:
                    return user32.CallNextHookEx(self.h_mouse, nCode, wParam, lParam)
                
                # Verarbeite nur Linksklicks
                if wParam == WM_LBUTTONDOWN:
                    if self.handle_mouse_event(x, y):
                        return 1  # Event unterdrücken
        except Exception as e:
            logging.error(f"Mouse-Hook Fehler: {e}")
        
        return user32.CallNextHookEx(self.h_mouse, nCode, wParam, lParam)

    def _keyboard_proc(self, nCode, wParam, lParam):
        try:
            if nCode == HC_ACTION and wParam == WM_KEYDOWN:
                info = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                # Nur für Debug: Tastenechos
        except Exception as e:
            logging.error(f"Keyboard-Hook Fehler: {e}")
        
        return user32.CallNextHookEx(self.h_keyboard, nCode, wParam, lParam)

    def start(self):
        """Startet die Anwendung"""
        # Starte Hook-Thread
        hook_thread = threading.Thread(target=self.hook_thread, daemon=True)
        hook_thread.start()
        
        logging.info("CheckCopy gestartet")
        
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            logging.info("Shutdown...")
            self.running = False
            hook_thread.join(timeout=2)

# ============================================================
# Einstiegspunkt
# ============================================================

if __name__ == "__main__":
    app = CheckCopyApp()
    app.start()
