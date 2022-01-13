# pymacromaker
Project to make macros that are crossplatform.

# dependencies
python 3  
pip  
pynput  

# pip installs

pip install pynput

# Usage:

Read keybinds in main.py, make macro.

# Example:
Macro format subject to change, but the sample_macro.txt shows what data the macros save.  
If using ubuntu, move terminal to be the top second icon in pinned application bar, comment out make macro, in main.py, and the demo will play.

# Known issues:

Typing too fast will cause keys to be skipped due to the previous key's release event not triggering before the next key's detection can begin(WPM past 70-80 will cause problems based on my testing.)

No way to currently do combination key press, keys that require shift key for exmaple, will enter the key, but if you want something like ctrl + c, it will only press the last released key. 