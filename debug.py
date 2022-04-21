from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener

def listen_start():    
    keyboard_listener.start()
    mouse_listener.start()
    keyboard_listener.join()
    mouse_listener.join()
    print("both threads killed")

#Stop listening for keyboard presses/mouse presses
def listen_stop():
    print("THE THREAD STOPPED")

    mouse_listener.stop()
    keyboard_listener.stop()

def _on_press( input_key):
    print("press!")
    listen_stop()

def _on_release(input_key):    
    pass
def _on_click( mouse_x, mouse_y, button, click):
    print('click!')
    listen_stop()


keyboard_listener = KeyboardListener(on_press=_on_press, on_release=_on_release)
mouse_listener = MouseListener(on_click=_on_click)

listen_start()