from pynput import keyboard, mouse
import time

mouse_controller = mouse.Controller()

record = False
copy = False
clickPos = [None, None]
clickIndex = 0
copying = False

print("drücke F9 zum Aufnehmen oder F10 für Copy-Modus")

def keyCall(key):
    global record, copy, clickPos, clickIndex
    if key == keyboard.Key.f9:
        record = True
        copy = False
        clickPos = [None, None] #reset positions
        clickIndex = 0          #reset index
        print("Record mode: click 2 positions")
    elif key == keyboard.Key.f10:
        if clickPos[0] is None or clickPos[1] is None:
            print("Bitte zuerst zwei Positionen aufnehmen.")    #verhindert Copy-Modus ohne gespeicherte Positionen
            return
        copy = True
        record = False
        print("Copy mode active")

def recordClicks(x, y, button, pressed):
    global clickPos, clickIndex, record
    if not pressed or button != mouse.Button.left:
        return
    if clickIndex < 2:
        clickPos[clickIndex] = x
        print(f"Saved x{clickIndex + 1}: {clickPos[clickIndex]}")
        clickIndex += 1
        if clickIndex == 2:
            record = False
            print("Positions ready:", clickPos)


def do_copy(y):
    global copying
    try:
        print("maus kopiert zu", clickPos[0], clickPos[1])

        mouse_controller.position = (clickPos[0], y)
        mouse_controller.click(mouse.Button.left, 1)
        print("click 1 beim x=", clickPos[0], "y=", y)
        time.sleep(0.05)

        mouse_controller.position = (clickPos[1], y)
        mouse_controller.click(mouse.Button.left, 1)
        print("click 2 beim x=", clickPos[1], "y=", y)

        time.sleep(0.05)
    except Exception as e:
        print("Copy error:", repr(e))
    finally:
        copying = False


def copyClicks(y):
    global copying
    if clickPos[0] is None or clickPos[1] is None:
        print("Fehler: Positionen nicht gespeichert")
        return

    print("copyClicks called")
    copying = True
    do_copy(y)


def clickCall(x, y, button, pressed):
    global copying, record, copy

    if not pressed or button != mouse.Button.left:
        return

    print(f"click detected: x={x}, y={y}, mode=record={record}, copy={copy}, copying={copying}")

    if copying:
        print("  (synthetic click ignored)")
        return

    if record:
        recordClicks(x, y, button, pressed)
    elif copy:
        copyClicks(y)
        copyClicks(y)
    else:
        print("kein Modus aktiv")

with keyboard.Listener(on_press=keyCall) as kb, \
    mouse.Listener(on_click=clickCall) as ms:
    kb.join()
    ms.join()
