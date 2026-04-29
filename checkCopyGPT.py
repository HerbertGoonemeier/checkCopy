from pynput import mouse, keyboard
import threading
import time

mouse_controller = mouse.Controller()

mode = "idle"
positions = []
copying = False

print("F9 = record | F10 = copy | ESC = exit")

# -------------------------
# KEYBOARD
# -------------------------
def on_key(key):
    global mode, positions

    if key == keyboard.Key.f9:
        mode = "record"
        positions = []
        print("Record mode: click 2 positions")

    elif key == keyboard.Key.f10:
        if len(positions) < 2:
            print("Need 2 positions first!")
            return
        mode = "copy"
        print("Copy mode active")

    elif key == keyboard.Key.esc:
        print("Exit")
        return False


# -------------------------
# COPY WORKER (thread)
# -------------------------
def do_copy(y):
    global copying

    try:
        x1, x2 = positions

        print(f"Copying click at y={y} to x={x1} and x={x2}")

        mouse_controller.position = (x1, y)
        mouse_controller.click(mouse.Button.left, 1)
        time.sleep(0.05)

        mouse_controller.position = (x2, y)
        mouse_controller.click(mouse.Button.left, 1)
    finally:
        copying = False


# -------------------------
# MOUSE HANDLER
# -------------------------
def on_click(x, y, button, pressed):
    global positions, copying

    if not pressed or button != mouse.Button.left:
        return

    if copying:
        return

    # RECORD MODE
    if mode == "record":
        if len(positions) < 2:
            positions.append(x)
            print(f"Saved: {x}")

            if len(positions) == 2:
                print("Positions ready:", positions)

    # COPY MODE
    elif mode == "copy":
        if len(positions) < 2:
            print("No positions stored")
            return

        copying = True
        threading.Thread(target=do_copy, args=(y,), daemon=True).start()


# -------------------------
# START LISTENERS
# -------------------------
with keyboard.Listener(on_press=on_key) as kb, \
     mouse.Listener(on_click=on_click) as ms:
    kb.join()
    ms.join()