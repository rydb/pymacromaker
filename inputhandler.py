"""
DO NOT RUN THIS INSIDE A VIRTUAL ENVIORMENT, THIS WILL BREAK IF YOU DO. I DO NOT KNOW WHY
"""




import time
import os

#For annotation
from typing import List

#For error handling
import traceback

from pynput import keyboard as Keyboard
#Import controllers to simulate keyboard and mouse movements of recorded keys
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Listener as KeyboardListener
from pynput.keyboard import Key
#Import listeners to listen to keyboard/mouse inputs
from pynput.mouse import Button, Controller as MouseController
from pynput.mouse import Listener as MouseListener
from sys import platform

def _get_os_config_directory() -> str:
    #directory where macros and keybins are stored. initialized with illegial characters to stop accidental macros being stored in root...
    set_os_macroconfig_store = "!?[]{]\""

    if platform == "linux" or platform == "linux2":
        set_os_macroconfig_store = os.environ['HOME'] + "/.local/pymacromaker"
        pass
        # linux
    elif platform == "darwin":
        raise Exception("No keybind/macro directory set for this OS X. Fix that then remove this exception")
        pass
        # OS X
    elif platform == "win32":
        raise Exception("No keybind/macro directory set for windows. Fix that then remove this exception.")
        pass
    else:
        raise Exception("Huh, what OS is this? Anyway, no keybind/macro directory set for this OS. ")
        # Windows...
    return set_os_macroconfig_store

place_to_round_to = 2

#print debug stuff if true
debug = False

#Keys which are ignored due to them being used to input other keys(caps lock, shift, etc..), or by merit of them being inconsistent
ignored_keys = ["Key.shift"]

#For some reason, pynput doesnt have an internal dictionary to convert non alphabetic keys to pynput presses, so I need to make a dictionary to do that..
key_to_object_dict = {
    #non alpha keys
    "Key.enter": Key.enter,
    "Key.ctrl": Key.ctrl,
    "Key.ctrl_r": Key.ctrl_r,
    "Key.space": Key.space,
    "Key.tab": Key.tab,
    "Button.left": Button.left,
    "Button.right": Button.right
}

#Sometimes, when keys are pressed and released, the press event is not caught due to typing too fast/other factors. this is the value the hold duration defaults to if that happens.
default_press_hold_if_press_event_not_triggered = 0.1

#nice website to test keypresses/durations:
#https://www.onlinepianist.com/virtual-piano

class key_presses():
    """ Object keypresses are stored in
    
    mouse/keyboard use pynput mouse/keyboard control. See: https://www.tutorialspoint.com/how-to-control-your-mouse-and-keyboard-using-the-pynput-library-in-python

    hold_duration_s: how long key is held for in s
    key: the key it self, stored as a string/keyboard/mouse object. Read as a string and do not modify.
    press_end_time_at_epoch: Used for press_stored_key, see there for details.
    """
    def __init__(self):

        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        #how long the key/click was help down for.
        self.hold_duration_s = 0.0
        
        self.keys= None

        #Mouse pos at time of click/press
        self.mouse_pos_xy = None

        #(If enabled) track when keypress ended at time epoch, so that another key that comes after, it will wait for the duration of time the user waited
        self.press_end_time_at_epoch = 0

        #Control type, weather the key is a mouse key or a keyboard key. determiens how the program should handle simulating inputs
        self._control_type = None

        self.keyboard_listener = KeyboardListener(on_press=self._on_press, on_release=self._on_release)
        self.mouse_listener = MouseListener(on_click=self._on_click)
        
    def __str__(self):
        return str(self._control_type) + " " + str(self.keys) + " " + str(self.hold_duration_s) + " " + str(self.press_end_time_at_epoch) + " " + str(self.mouse_pos_xy)

    def __repr__(self):
        return str(self._control_type) + " " + str(self.keys) + " " + str(self.hold_duration_s) + " " + str(self.press_end_time_at_epoch) + " " + str(self.mouse_pos_xy)


    def press_stored_key(self, epoch_time_to_wait_before_press=0, hold_duration_override=0):
        """ 
        press a stored keypress based on how it was pressed when they object that represents its keypressed was stored.

        This method handles the finickyness of pynput keypresses, and also has optional perameters for modifiers on how/when to press keys
         1. epoch_time_to_wait_before_press: Pass a different key's "press_end_time_at_epoch", and the key will wait to press for the duration of time between when the two keys were pressed.
         simulate user input delay
         2. hold_duration_override: override the durration of time the original keypress was held down for, and instead hold it down for the time the override time in seconds. Keep at 0 for no
         override
        
        NOTE: Currently, "epoch_time_to_wait_before_press" is experimental, and I havent found a way to get the sleep difference between the times to be accurate. there is a small but noticable
        delay, that gets worse the larger you hold the key down for, and im not sure how to fix it.
        """
        if(hold_duration_override != 0):
            self.hold_duration_s = hold_duration_override

        #Prevent accidental pressing of mouse key by releasing the mouse key press
        self.mouse.release(Button.left)
        self.mouse.release(Button.right)

        if(self._control_type == "Mouse"):            

            self.mouse.position = self.mouse_pos_xy

            if(epoch_time_to_wait_before_press != 0):
                if(debug == True):
                    print("waiting + " + str(self.press_end_time_at_epoch - epoch_time_to_wait_before_press))    
                time.sleep(self.press_end_time_at_epoch - epoch_time_to_wait_before_press)
            #if(debug):
            #    print(type(self.keys))
            self.mouse.press(self.keys)
            time.sleep(self.hold_duration_s)
            self.mouse.release(self.keys)
        elif(self._control_type == "Keyboard"):
            
            self.mouse.position = self.mouse_pos_xy
            try:
                if(epoch_time_to_wait_before_press != 0):
                    if debug == True:
                        print("waiting + " + str(self.press_end_time_at_epoch - epoch_time_to_wait_before_press))    
                        time.sleep(self.press_end_time_at_epoch - epoch_time_to_wait_before_press)

                self.keyboard.press(self.keys)
                time.sleep(self.hold_duration_s)
                self.keyboard.release(self.keys)
            except Exception as e:
                print("ran into error for keyboard press.")
                print("Actual error: " + traceback.format_exc() )
        else:
            raise Exception("Unknown control type: entered control type: " + str(self._control_type))
    
    #start listening for presses/mouse presses
    def listen_start(self):    
        """To start listening for a keypress, call this method.
        Once a keypress/mouse-click is detected, relevant information about when the key was pressed, how long, and where, etc.. is stored inside the Key object used to call this method."""
        self.keyboard_listener.start()
        self.mouse_listener.start()
        self.keyboard_listener.join()
        self.mouse_listener.join()

    #Stop listening for keyboard presses/mouse presses
    def _listen_stop(self):
        self.mouse_listener.stop()
        self.keyboard_listener.stop()


    def _on_press(self, input_key):
        """
        method that is called when a keyboard keypress is detected. 
        """
        if(ignored_keys.__contains__(str(input_key))):
            pass
        else:
            #print(str(input_key) + 'key pressed')
            
            if(str(input_key ) == "Key.shift"):
                print("shifting key")

            if self.hold_duration_s == 0:
                self.hold_duration_s = time.time()


    def _on_release(self, input_key):    
        #print(str(input_key) + "key released")
        
        if(ignored_keys.__contains__(str(input_key))):
            pass
            #print(str(input_key) + " was released, but is classed as a key to ignore. Will not be entered as a part of the macro.")
        else:
            self._control_type, self.keys, self.hold_duration_s, self.press_end_time_at_epoch, self.mouse_pos_xy = "Keyboard", input_key, round(time.time() - self.hold_duration_s, place_to_round_to), time.time(), self.mouse.position
            
            if(debug):
                print(self._control_type + " pressed, current key is now set to " + str(self))
            
            #sometimes, if you type keys too fast, the press event for the key is not triggered and its only caught as a release. this sets it to 0.1 seconds by default
            if(self.hold_duration_s > 999999):
                print("press event not triggered, setting keypress duration to " + str(default_press_hold_if_press_event_not_triggered) + " seconds")
                self.hold_duration_s = default_press_hold_if_press_event_not_triggered
        
            self._listen_stop()
   
    def _on_click(self, mouse_x, mouse_y, button, click):
        
        
        if(click):
            self.captured_time = time.time()
            self.hold_duration_s = self.captured_time
            
        else:
            self.press_end_time_at_epoch = self.captured_time

            self._control_type, self.keys, self.hold_duration_s, self.press_end_time_at_epoch, self.mouse_pos_xy = "Mouse", button, round(time.time() - self.hold_duration_s, place_to_round_to), time.time(), self.mouse.position
            self._listen_stop()

            if(debug):
                print(self._control_type + " pressed, current key is now set to " + str(self))
        
def save_macro(name, keys_to_store: List[key_presses]):
    """Save macros in /macros folder in the same directory as input handler."""
    #Store macro same directory as python file is being executed in
    name = _get_os_config_directory() + "/macros/" + name
    with open((name + '.txt'), 'w') as filehandle:
        for listitem in keys_to_store:
            #Keycodes encase alphabetical characters in single quotes, I.E, e becomes 'e'. this needs to be removed becasue pynput cant read its own formating.
            listitem = str(listitem).replace("'", "")
            filehandle.write('%s\n' % listitem)

#Construct macro(keypress list) based on saved macro file.
def load_macro(name) -> List[key_presses]:
    """
    Load macros in /macros folder in the same directory as input handler.
    exclude file extension
    """

    #Macro list to construct
    current_macro = []
    try:
        with open((_get_os_config_directory() + name + '.txt'), 'r') as filehandle:
            for line in filehandle:
                constructed_key = key_presses()
                # remove linebreak which is the last character of the string

                #also strip all uneeded characters in string when reading macro
                currentLine = [s.strip("(),") for s in line[:-1].split(" ")]
                if(debug):
                    print("<<MACRO LOAD>> current read line is: " + str(currentLine))
                constructed_key._control_type = currentLine[0]
                #constructed_key.key.key_object = currentLine[1]
                
                if(debug):
                    print("<<MACRO LOAD>> input delay is: " + currentLine[2])
                constructed_key.hold_duration_s = float(currentLine[2])

                #Correlate non-alphabetical key-codes to their pynput counterpart via dictionary containing them, if that fails, assign to macro list as string(will work for alphabetical characters)
                try:              
                    constructed_key.keys = key_to_object_dict[currentLine[1]]
                    print(constructed_key.keys)
                except:
                    print(currentLine[1])
                    constructed_key.keys = currentLine[1]
                    pass
                if(debug):
                    print("<<MACRO LOAD>> key press ended at time epoch of: " + currentLine[3])

                constructed_key.press_end_time_at_epoch = float(currentLine[3])
                constructed_key.mouse_pos_xy = (int(currentLine[-2]), int(currentLine[-1]))

                if(debug):
                    print("<<MACRO LOAD>> final constructed key is: " + str(constructed_key))
                current_macro.append(constructed_key)
    except Exception as e:
        print("<<MACRO LOAD>> ran into error constructing macro, investigate.")
        print("<<MACRO LOAD>> Actual error: " + traceback.format_exc())

    print(current_macro)
    return current_macro
