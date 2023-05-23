import tkinter.dnd
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import random
import time
import cv2.data
import numpy as np
import PIL
from PIL import ImageTk, Image
from cv2 import *


photo = "" #FOR RESIZING AND SHOW

class ChangesList:
    changes_list = []

    def add_algorithm(self, alg_name, option1, option2, image):
        if option1 == 0 and option2 == 0 and alg_name != "shuffle":
            return
        for item in self.changes_list:
            if item[0] == alg_name:
                self.changes_list.remove(item)
        self.changes_list.append([alg_name, option1, option2, image])

    def get_last_image(self):
        if len(self.changes_list)==0:
            return

        original_image = self.changes_list[0][3]
        for item in self.changes_list:
            if item[0] == "alg1":
                original_image = algorithm1(original_image, item[1], item[2])
            if item[0] == "alg2":
                original_image = algorithm2(original_image, item[1], item[2])
            if item[0] == "alg3":
                original_image = algorithm3(original_image, item[1], item[2])
            if item[0] == "shuffle":
                original_image = channel_shuffle(original_image, item[1])
        return original_image

    def alg_last_option(self, alg_name):
        for item in self.changes_list:
            if item[0] == alg_name:
                return [item[1], item[2]]
        return []


    def save_picture(self, path):
        self.get_last_image(self).save(path)
        
all_changes = ChangesList

def upload_photo():
    all_changes.changes_list = []
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=[("Image", ".jpeg"),
                                                     ("Image", ".jpg"),
                                                     ("Image", ".png")])
    if filename:
        listbox["state"] = ["readonly"]
        strength["state"] = ["normal"]
        power["state"] = ["normal"]
        save_button["state"] = ["normal"]
        channel_shuffle_button["state"] = ["normal"]
        all_changes.add_algorithm(ChangesList, "new", 1, 1, Image.open(filename))
        show_photo()

def channel_shuffle(image, ch_array):
    array_image = np.array(image, dtype=np.uint8)
    for i in range(array_image.shape[0]):
        for j in range(array_image.shape[1]):
            r = array_image[i][j][0]
            g = array_image[i][j][1]
            b = array_image[i][j][2]
            array_image[i][j][ch_array[0]] = r
            array_image[i][j][ch_array[1]] = g
            array_image[i][j][ch_array[2]] = b

    result = Image.fromarray(array_image)
    return result



def button_shuffle(image, ch_array):
    random.shuffle(ch_array)
    if len(all_changes.changes_list) == 0:
        return
    else:
        all_changes.add_algorithm(ChangesList, "shuffle", ch_array, power.get(), channel_shuffle(image, ch_array))
        show_photo()


def algorithm1(image, pos1, pos2):
    if pos1 == 0 or pos2 == 0:
        return image

    array_image = np.array(image, dtype=np.uint8)

    normal_distribution = np.random.normal(0, pos1 * pos2, array_image.shape)
    normal_distribution_img = array_image + normal_distribution.astype(np.uint8)
    result = Image.fromarray(normal_distribution_img)
    return result

def algorithm2(image, pos1, pos2):
    if pos1 == 0:
        return image
    array_image = np.array(image, dtype=np.uint8)
    gaussian_noise = np.zeros(array_image.shape, dtype=np.uint8)
    cv2.randn(gaussian_noise, pos1, pos2*100)
    gaussian_noise = gaussian_noise.astype(np.uint8)
    gaussian_noise_img = cv2.add(array_image, gaussian_noise)
    result = Image.fromarray(gaussian_noise_img)
    return result


def algorithm3(image, pos1, pos2):
    if pos2 == 0:
        return image
    array_image = np.array(image, dtype=np.uint8)

    s = pos2
    for i in range(array_image.shape[0]):
        for j in range(array_image.shape[1]):
            rdn = random.random()
            if rdn < s:
                array_image[i][j] = 0
            elif rdn > 1 - s:
                array_image[i][j] = 255

    result = Image.fromarray(array_image)
    return result


def listbox_event(event):
    noise_type = listbox.get()
    if noise_type == noises_list[0]:
        option_setter("alg1")
    if noise_type == noises_list[1]:
        option_setter("alg2")
    if noise_type == noises_list[2]:
        option_setter("alg3")
    listbox_event_func(noise_type)


def listbox_event_func(noise_type):
    pos1 = strength.get()
    pos2 = power.get()
    if noise_type == noises_list[0]:
        all_changes.add_algorithm(ChangesList, "alg1", pos1, pos2,
                                  algorithm1(all_changes.get_last_image(ChangesList), pos1, pos2))
    elif noise_type == noises_list[1]:
        all_changes.add_algorithm(ChangesList, "alg2", pos1, pos2,
                                  algorithm2(all_changes.get_last_image(ChangesList), pos1, pos2))
    elif noise_type == noises_list[2]:
        all_changes.add_algorithm(ChangesList, "alg3", pos1, pos2,
                                  algorithm3(all_changes.get_last_image(ChangesList), pos1, pos2))
    show_photo()


def option_setter(alg_name):
    options = all_changes.alg_last_option(ChangesList, alg_name)
    if len(options) == 2:
        strength.set(value=options[0])
        power.set(value=options[1])
    else:
        strength.set(value=0)
        power.set(value=0)

def scale_event(event):
    listbox_event_func(listbox.get())

def show_photo():
    global photo
    photo = ImageTk.PhotoImage(all_changes.get_last_image(ChangesList).
                               resize((int(window_width * photo_relwidth), int(window_height * photo_relheight)),
                                      Image.NEAREST))

    canvas.create_image(0, 0, image=photo, anchor="nw")


def save_photo():
    filename = filedialog.asksaveasfile(initialdir="/",
                                        title="Select a File",
                                        defaultextension="*.png",
                                        filetypes=[("JPEG", "*.jpeg"), ("PNG", "*.png"), ("JPG", "*.jpg")])
    if filename:
        all_changes.save_picture(ChangesList, filename.name)


window_width = 1400
window_height = 800

root = Tk()
root.title("Генератор шумов")
root.geometry(f'{window_width}x{window_height}')
noises_list = ["Normal Distribution", "Gaussan", "Salt & Pepper"]
noise_start_position = StringVar(value=noises_list[0])
root.resizable(width=False, height=False)


main_frame = Frame(root)
main_frame.place(relwidth=window_width,
                  relheight=window_height)

photo_frame = Frame(root, bg="black")
photo_relwidth = 0.745
photo_relheight = 0.9
photo_relx = 0.25
photo_rely = 0.05

photo_frame.place(relwidth=photo_relwidth,
                  relheight=photo_relheight,
                  relx=photo_relx,
                  rely=photo_rely)

navigation_frame = Frame(root)
navigation_relwidth = photo_relx
navigation_relheight = photo_relheight
navigation_relx = 0
navigation_rely = photo_rely

navigation_frame.place(relwidth=navigation_relwidth,
                       relheight=navigation_relheight,
                       relx=navigation_relx,
                       rely=navigation_rely)

title = Label(navigation_frame,
              text="Генератор шума",
              font="Montserrat 25")
title.pack(fill="x")

listbox = ttk.Combobox(navigation_frame,
                       values=noises_list,
                       textvariable=noise_start_position,
                       font="Montserrat 16",
                       state=["disabled"],
                       width=20,
                       height=26)

listbox.bind('<<ComboboxSelected>>', listbox_event)
listbox.pack(pady=20)

strength_text = Label(navigation_frame,
                      text="Strength",
                      font="Montserrat 12")
strength_text.pack(anchor="w", padx=20)

strength = Scale(navigation_frame,
                 orient=HORIZONTAL,
                 from_=0,
                 to=100,
                 length=297,
                 command=scale_event,
                 state="disabled")
strength.pack()

power_text = Label(navigation_frame,
                      text="Power",
                      font="Montserrat 12")
power_text.pack(anchor="w", padx=20)

power = Scale(navigation_frame,
                 orient=HORIZONTAL,
                 from_=0.0,
                 to=1.0,
                 length=297,
                 command=scale_event,
                 state="disabled",
                 resolution=0.01)
power.pack()

channels_array = [0, 1, 2]
random.shuffle(channels_array)

channel_shuffle_button = Button(navigation_frame,
                text="ChannelShuffle",
                font="Montserrat 14",
                height=1,
                state="disabled",
                command=lambda: button_shuffle(all_changes.get_last_image(ChangesList), channels_array),
                width=26)
channel_shuffle_button.pack(anchor="s")

canvas = Canvas(photo_frame, width=1900, height=900, bg="grey")
canvas.pack()

save_button = Button(navigation_frame,
                text="SAVE",
                font="Montserrat 14",
                command=save_photo,
                height=1,
                width=4,
                bg="lightblue",
                state="disabled")
save_button.pack(side=RIGHT, anchor="s")

upload_button = Button(navigation_frame,
                text="↓ LOAD ↓",
                font="Montserrat 14",
                command=upload_photo,
                height=1,
                width=26)
upload_button.pack(side=LEFT, anchor="s")


root.mainloop()