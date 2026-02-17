from pynput import mouse, keyboard
import time

#variablen hier definiert
click_Pos = []  #array > speichert die x,y-Wertepaare der Maus-position
record = False  #bool > variable steuert Aufnahme True > wird aufgenommen, False wird nicht aufgenommen
pressedKey

#funktionen/Listener für callback hier definiert
def recordKey(key): #Funktion registriert Tastatureingaben
    global record #anscheinend muss man in python definieren dass man die variable global ändert?
    try
        if key.char.lower = "r": #schaut ob normale Taste gedrückt wurde
            record = not record #switch für record, wenn True + "R" > False, wenn False + "R" dann True
            if record = True:
                print("Aufnahme startet")
            else:
                print("Aufnahme stoppt")

        else:
            print("falsche Taste") #Userhinweis
    except AttributeError:
        pass


with keyboard.Listener(...=recordKey) as Listener #Listener ruft die Funktion auf sobald sie benötigt wird
    Listener.join() #lässt Listener laufen auch nach einmaliger ausführung

def recordClicks(x, y, button, pressed): #Funktion liest Mausklicks
    if record == True and pressed = True:
        click_Pos.append((x,y))
        print("Pos",x,y)

with mouse.Listener(on_click=recordClicks) as Listener: #Listener ruft die Funktion auf sobald sie benötigt wird
    Listener.join() #lässt Listener laufen auch nach einmaliger ausführung

### Pogramm dass in Laufzeit ausgeführt wird
print("drücke R zum aufnehmen")

