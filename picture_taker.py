#for keybinds
import inputhandler as keyhandler

#For image cropping
import cv2
import pyautogui

#for checking for images for overwriting/deleting
from os.path import exists
from os import remove

#for converting from img to pdf
from PIL import Image

#key = keyhandler.key_presses()

#key.listen_start()


#Create macro to capture portion of screen bounded by xy of top left and bottom right of fed mouse positions to take single/multiple pictures. 
def bound_capture_clip(img_dir="/home/rydb/Desktop/picture_taker_test", pdf_name="pictures", xy1=[], xy2=[]):
    #Desired picture file format:
    picture_format = ".png"


    if xy1 == [] and xy2 == []:
        print("no bounding box fed for pictures. Left click top left and bottom right bound for photo. Press any other key to reset. ")

        print("also, make sure your bounding box has boundries that don't overlap, so errors are not caused. ")

        print("press ctrl to start")
        while True:
            key1 = keyhandler.key_presses()
            key1.listen_start()
            key_str1 = str(key1.keys)
            print(key_str1)
            if(key_str1 == "Key.ctrl"):
                break
        while True:
            print('click position for top left')
            #Upper left bound of window area
            key1 = keyhandler.key_presses()
            key1.listen_start()
            key_str1 = str(key1.keys)
            if(key_str1 == "Button.left"):
                xy1 = key1.mouse_pos_xy
            
            #Bottom right bound of window area
            print("click position for top right")
            key2 = keyhandler.key_presses()
            key2.listen_start()
            key_str2 = str(key2.keys)
            if(key_str2 == "Button.left"):
                xy2 = key2.mouse_pos_xy

            print(str(xy1) + str(xy2) + " cords taken. Press e screen shot, press r when finished")
            break

    #Current index of pictures taken.
    pic_count = 1
    picture_list = []
    while True:

        key = keyhandler.key_presses()
        key.listen_start()
        key_str = str(key.keys)
        #Take snapshot, and clip based on left and right clicked area
        if(key_str == "\'e\'"):
            print("picture taken")
            #Take screenshot, and clip with cv2
            pic = img_dir + "/pic" + str(pic_count) + picture_format
            
            #append file directory of picture for pdf conversion later
            picture_list.append(pic)
            #remove previous picture with same name to prevent errors with OpenCV. 
            if(exists(pic)):
                remove(pic)
            pyautogui.screenshot(pic)
            img = cv2.imread(pic)
            #cv2.imshow("img before cropping", img)
            #cv2.waitKey(0)
            #print(img)
            
            #crop an opencv image based on dimensions, and overwrite old picture with cropped one. 
            img = img[xy1[1]:xy2[1], xy1[0]:xy2[0]]
            cv2.imwrite(pic, img)
            pic_count += 1

        if(key_str == "\'r\'"):
            if picture_list == []:
                print("no pictures in picture list, ignoring keypress")
                continue

            print(str(pic_count) + " total pictures taken. Converting them to pdf.")

            images = [
                Image.open(f) for f in picture_list
            ]
            pdf_path = img_dir + "/" + pdf_name + ".pdf"

            images[0].save(
                pdf_path, "PDF" ,resolution=100.0, save_all=True, append_images=images[1:]
            )
            break
    
#single character keys have ' symbol in them, so they need to be included in single character key checks
#if(str(key.keys) == '\'e\''):
#    print("pressed e")

bound_capture_clip()
#if(str(key.keys) == "Key.ctrl"):
