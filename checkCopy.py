from pynput import mouse, keyboard
from pynput.mouse import Controller, Button
import time

#variablen hier definiert
click_Pos = []  #array > speichert die x,y-Wertepaare der Maus-position
record = False  #bool > variable steuert Aufnahme True > wird aufgenommen, False wird nicht aufgenommen

mouse = Controller()

'''
scroll_dy = []      #scroll-inkrement
scroll_total = 0    #scroll-absolut
'''
#funktionen/Listener für callback hier definiert
def recordKey(key): #Funktion registriert Tastatureingaben
    global record #anscheinend muss man in python definieren dass man die variable global ändert?
    try:
        if key.char.lower() == "r": #schaut ob normale Taste gedrückt wurde
            record = not record #switch für record, wenn True + "R" > False, wenn False + "R" dann True
            if record == True:
                print("Aufnahme startet")
            else:
                print("Aufnahme stoppt")
        else:
            print("falsche Taste") #Userhinweis
    except AttributeError:
        pass


keyboard_listener = keyboard.Listener(on_press=recordKey)
keyboard_listener.start()

def recordClicks(x, y, button, pressed): #Funktion liest Mausklicks
    if record == True and pressed == True:
        click_Pos.append((x,y))
        print("Pos",x,y)

with mouse.Listener(on_click=recordClicks) as listener: #Listener ruft die Funktion auf sobald sie benötigt wird
    listener.join() #lässt Listener laufen auch nach einmaliger ausführung

'''
def recordScroll(x, y, dx, dy):
    global scroll_total
    if record == True:
        scroll_dy.append(dy)
        scroll_total = scroll_total + dy

with mouse.Listener(on_scroll=recordScroll) as Listener:
    Listener.join()
'''
### Pogramm dass in Laufzeit ausgeführt wird
print("drücke R zum aufnehmen")
print("\ndrücke R um die Aufzeichnung zu beenden")

for x,y in click_Pos:
    mouse.position = (x,y)
    mouse.click(Button.left)
    print(x,y)
    print("\nclicked")
    time.sleep(0.05)





