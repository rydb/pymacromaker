from inputhandler import key_presses, load_macro, save_macro
import numpy

Keybinds = {
    "start|stop_recording": "Key.ctrl",
    "continue|pause_recording": "*"

}

def key_as_string(key):
    return str(key).replace("'", "")

def make_macro(macro_name):
    key_list = []
    recording_paused = False
    print("Macro recording started, check keybinds for what does what. ")
    while True:
        key = key_presses()
        key.listen_start()
        pressed_key = key_as_string(key.keys)
        print(pressed_key)
        
        
        if pressed_key == Keybinds["start|stop_recording"]:
            print('macro recording stopped')
            break
        if(recording_paused):
            if pressed_key == Keybinds["continue|pause_recording"]:
                print("macro recording unpaused")
                recording_paused = False
        else:
            if pressed_key == Keybinds["continue|pause_recording"]:
                print("macro recording paused")
                recording_paused = True
                continue    
            key_list.append(key)
        #key.key

    save_macro(macro_name, key_list)

def play_macro(macro_name):
    previous_key_time = 0
    for key in load_macro(macro_name):
        print(key)
        key.press_stored_key(epoch_time_to_wait_before_press=previous_key_time)
        previous_key_time = key.press_end_time_at_epoch


make_macro("sample macro")
play_macro("sample macro")