# Code by Bernard Gorzkowski
# Contact: bernard.gorzkowski@gmail.com

import numpy as np
import os
from datetime import datetime

from PIL import ImageTk, Image
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilenames
from tkinter.filedialog import asksaveasfilename
from tkinter.simpledialog import Dialog


################################################################################
###### Generate noisy image from an initial distribution #####
################################################################################


###### Functions and classes #####


class AskYesNoCheck(Dialog):

    def __init__(self, parent, title = '', message = ''):
        self.message = message
        super().__init__(parent,title)
        
    # override body() to build your input form
    def body(self, master):
        self.var =tk.IntVar()
        tk.Label(master, text=self.message).pack(fill="x")
        tk.Checkbutton(master, text="Apply answer to all conflicts", variable = self.var, anchor="w").pack(fill="x")

    # override buttonbox() to create your action buttons
    def buttonbox(self):
        box = tk.Frame(self)
        tk.Button(box, text="Yes", width=10, command=self.yes, default=tk.ACTIVE).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(box, text="No", width=10, command=self.no).pack(side=tk.LEFT, padx=5, pady=5)
        box.pack()

    def yes(self):
        self.result = True
        self.ok()
    
    def no(self):
        self.result = False
        self.cancel()




def set_text(text, entry):
    entry.delete(0, tk.END)
    entry.insert(0, text)
    return

def set_output_folder_path(title, entry):
    path_folder = askdirectory(title=title)
    if path_folder == '':
        return
    set_text(path_folder, entry)

def set_paths_in_listbox(title, listbox):
    paths_image = askopenfilenames(title=title, filetypes=(("bmp file", "*.bmp"),("All Files", "*.*") ))
    if len(paths_image) == 0:
        return
    listbox.delete(0, tk.END)
    for index, path in enumerate(paths_image):
        listbox.insert(index, path)

def slider_callback(value, entry, log=False):
    if not log:
        set_text(value, entry)
    else:
        set_text(str(int(10**float(value))), entry)

def toggle_multiple_entry():
    if multiple_var.get() == 0:
        multiple_entry.configure(state="disabled")
    else:
        multiple_entry.configure(state="normal")


def generate_and_save_single_image(means_array, gaussian_mean, gaussian_std_deviation, path):
    saturation_value = int(saturation_entry.get())
    number_of_photons_to_trigger_event = int(event_trigger_entry.get())
    poisson_array = np.random.poisson(means_array)
    gaussian_noise = np.random.normal(gaussian_mean, gaussian_std_deviation, np.shape(means_array))

    noisy_array = poisson_array + gaussian_noise
    noisy_array[noisy_array < 0] = 0
    noisy_array = noisy_array//number_of_photons_to_trigger_event
    noisy_array[noisy_array > saturation_value] = saturation_value
    im = Image.fromarray(np.uint8(noisy_array))
    im.save(path)


def generate():

    number_of_images = image_listbox.size()

    if number_of_images == 0:
        tk.messagebox.showwarning(title="Warning", message="Please input images to noisify")
        return

    save_folder_path = save_entry.get()

    if save_folder_path == '':
        tk.messagebox.showwarning(title="Warning", message="Please specify a path for the output folder")
        return
    
    if not os.path.isdir(save_folder_path):
        tk.messagebox.showwarning(title="Warning", message='Folder "{}" does not exist'.format(save_folder_path))
        return
    
    poisson_photon_number = int(nbphoton_entry.get())
    gaussian_mean = float(gaussian_mean_entry.get())
    gaussian_std_deviation = float(gaussian_std_entry.get())


    number_of_saved_images = 0
    overwrite_file = False
    ask_for_permission = True


    multiple_images_box_checked = (multiple_var.get() == 1)
    if not multiple_images_box_checked:
        N = 1
    else:
        try:
            N = int(multiple_entry.get())
        except:
            N = -1
        if N <= 0:
            tk.messagebox.showwarning(title="Warning", message="Please enter a valid number of images")
            return
        if N*number_of_images > 9999:
            res = tk.messagebox.askquestion("Large number of images", "You are about to generate {} images, do you want to proceed ?".format(N*number_of_images))
            if (res=='no'):
                return

    for i in range(number_of_images):
        
        image_path = image_listbox.get(i)
        if not os.path.isfile(image_path):
            tk.messagebox.showwarning(title="Warning", message='File "{}" does not exist. Aborting image generation.'.format(image_path))
            return
        
        image_array = np.array(Image.open(image_path))
        means_array = poisson_photon_number*(image_array/np.sum(image_array))

        image_filename, image_file_extension = os.path.splitext(image_path)
        only_filename = os.path.basename(image_filename).split('/')[-1]

        number_of_digits = len(str(N))

        for j in range(1, N+1):
            if not multiple_images_box_checked:
                save_path = save_folder_path + '/' + only_filename + '_noisified' + image_file_extension
            else:
                save_path = save_folder_path + '/' + only_filename + '_noisified' + '_' + '0'*(number_of_digits - len(str(j))) + str(j) + image_file_extension

            if os.path.isfile(save_path) and ask_for_permission:
                dlg = AskYesNoCheck(root, title="File already exists", message = 'File "{}" already exists, do you want to overwrite it ?'.format(save_path))
                overwrite_file = dlg.result # yes/no answer
                if dlg.var.get() == 1: # "Apply answer to all conflicts"
                    ask_for_permission = False

            if not os.path.isfile(save_path) or overwrite_file:
                generate_and_save_single_image(means_array, gaussian_mean, gaussian_std_deviation, save_path)
                number_of_saved_images += 1

            progress.set(1000*(i*N + j)/(number_of_images*N))
            root.update_idletasks()
            
    tk.messagebox.showinfo(title="", message="Saved {} image{} in folder {}".format(number_of_saved_images, 's'*(not number_of_saved_images==1), save_folder_path))
    progress.set(0)


def export():
    output_path = save_entry.get()
    poisson_photon_number = int(nbphoton_entry.get())
    gaussian_mean = float(gaussian_mean_entry.get())
    gaussian_std_deviation = float(gaussian_std_entry.get())
    saturation = int(saturation_entry.get())
    number_of_photons_to_trigger_event = int(event_trigger_entry.get())

    now = datetime.now()
    dt_string = now.strftime("%Y/%m/%d %H:%M:%S")

    exported_file_path = asksaveasfilename(title="Export parameters as", filetypes=(("txt file", "*.txt"), ("All Files", "*.*")))
    if exported_file_path != '':
        f = open(exported_file_path, 'w')
        f.write("Parameters exported on " + dt_string)
        f.write("\n")
        f.write("\n")
        f.write("Output folder path: " + output_path)
        f.write("\n")
        f.write("Photon number: " + str(poisson_photon_number))
        f.write("\n")
        f.write("Gaussian mean: " + str(gaussian_mean))
        f.write("\n")
        f.write("Gaussian standard deviation: " + str(gaussian_std_deviation))
        f.write("\n")
        f.write("Saturation: " + str(saturation))
        f.write("\n")
        f.write("Number of photons to trigger event: " + str(number_of_photons_to_trigger_event))
        f.close()
        

###### Run the GUI #####


root = tk.Tk()
root.resizable(width=True, height=False)
root.title("Noisify")

# Image adres selector
image_label = tk.Label(root, text="Adresses of pictures to noisify:")
image_label.grid(row = 0, column = 0, columnspan = 3, pady = 2)

image_listbox = tk.Listbox(root, height = 5)
image_listbox.grid(row = 1, column = 0, rowspan = 2, columnspan = 2, padx = 4, pady = 2, sticky=tk.EW)

image_browse_button = tk.Button(root, text = "browse", command = lambda:set_paths_in_listbox("Select image to add noise to", image_listbox))
image_browse_button.grid(row = 1, column = 2, padx = 4, pady = 2, sticky=tk.W)

image_clear_button = tk.Button(root, text = "clear", command = lambda:image_listbox.delete(0, tk.END))
image_clear_button.grid(row = 2, column = 2, padx = 4, pady = 2, sticky=tk.W)

# Photon number selector
nbphoton_label = tk.Label(root, text="Average total number of photons (Poisson noise): ")
nbphoton_label.grid(row = 3, column = 0, columnspan = 3, pady = 2)

nbphoton_entry = tk.Entry(root)
nbphoton_entry.insert(0, '1000')
nbphoton_entry.grid(row = 4, column = 0, padx = 4, pady = 2)

nbphoton_slider = tk.Scale(root, from_ = 0, to = 7, digits = 4, resolution = 0.01, showvalue = False, orient = tk.HORIZONTAL, command=lambda value:slider_callback(value, nbphoton_entry, log=True))
nbphoton_slider.grid(row = 4, column = 1, columnspan = 2, padx = 4, pady = 2, sticky=tk.EW)
nbphoton_slider.set(3)

# Gaussian mean selector
gaussian_mean_label = tk.Label(root, text="Gaussian noise mean: ")
gaussian_mean_label.grid(row = 5, column = 0, columnspan = 3, pady = 2)

gaussian_mean_entry = tk.Entry(root)
gaussian_mean_entry.insert(0, '0')
gaussian_mean_entry.grid(row = 6, column = 0, padx = 4, pady = 2)

gaussian_mean_slider = tk.Scale(root, from_ = 0, to = 255, digits = 0, resolution = 1, showvalue = False, orient = tk.HORIZONTAL, command=lambda value:slider_callback(value, gaussian_mean_entry))
gaussian_mean_slider.grid(row = 6, column = 1, columnspan = 2, padx = 4, pady = 2, sticky=tk.EW)

# Gaussian standard deviation selector
gaussian_std_label = tk.Label(root, text="Gaussian noise standard deviation: ")
gaussian_std_label.grid(row = 7, column = 0, columnspan = 3, pady = 2)

gaussian_std_entry = tk.Entry(root)
gaussian_std_entry.insert(0, '1')
gaussian_std_entry.grid(row = 8, column = 0, padx = 4, pady = 2)

gaussian_std_slider = tk.Scale(root, from_ = 0, to = 15, digits = 3, resolution = 0.1, showvalue = False, orient = tk.HORIZONTAL, command=lambda value:slider_callback(value, gaussian_std_entry))
gaussian_std_slider.grid(row = 8, column = 1, columnspan = 2, padx = 4, pady = 2, sticky=tk.EW)
gaussian_std_slider.set(1)

# Saturation threshold selector
saturation_label = tk.Label(root, text="Saturation threshold: ")
saturation_label.grid(row = 9, column = 0, columnspan = 3, pady = 2)

saturation_entry = tk.Entry(root)
saturation_entry.insert(0, '255')
saturation_entry.grid(row = 10, column = 0, padx = 4, pady = 2)

saturation_slider = tk.Scale(root, from_ = 1, to = 255, digits = 0, resolution = 1, showvalue = False, orient = tk.HORIZONTAL, command=lambda value:slider_callback(value, saturation_entry))
saturation_slider.grid(row = 10, column = 1, columnspan = 2, padx = 4, pady = 2, sticky=tk.EW)
saturation_slider.set(255)

# Number of photons to trigger event selector
event_trigger_label = tk.Label(root, text="Number of photons to trigger event: ")
event_trigger_label.grid(row = 11, column = 0, columnspan = 3, pady = 2)

event_trigger_entry = tk.Entry(root)
event_trigger_entry.insert(0, '1')
event_trigger_entry.grid(row = 12, column = 0, padx = 4, pady = 2)

event_trigger_slider = tk.Scale(root, from_ = 1, to = 100, digits = 0, resolution = 1, showvalue = False, orient = tk.HORIZONTAL, command=lambda value:slider_callback(value, event_trigger_entry))
event_trigger_slider.grid(row = 12, column = 1, columnspan = 2, padx = 4, pady = 2, sticky=tk.EW)
event_trigger_slider.set(1)

# Save as selector
save_label = tk.Label(root, text="Select folder to save generated images:")
save_label.grid(row = 13, column = 0, columnspan = 3, pady = 2)

save_entry = tk.Entry(root)
save_entry.grid(row = 14, column = 0, columnspan = 2, padx = 4, pady = 2, sticky=tk.EW)

save_button = tk.Button(root, text = "browse", command = lambda:set_output_folder_path("Save as", save_entry))
save_button.grid(row = 14, column = 2, padx = 4, pady = 2, sticky=tk.W)


# Multiple images option
multiple_label = tk.Label(root, text="Generate multiple images")
multiple_label.grid(row = 15, column = 0, columnspan = 3, pady = 2)

multiple_var = tk.IntVar()
multiple_checkbox = tk.Checkbutton(root, variable = multiple_var, command = toggle_multiple_entry)
multiple_checkbox.grid(row = 16, column = 0, padx = 4, pady = 2, sticky = tk.E)

multiple_info_label = tk.Label(root, text = "Number of images:")
multiple_info_label.grid(row = 16, column = 1, padx = 4, pady = 2)

multiple_entry = tk.Entry(root)
multiple_entry.grid(row = 16, column = 2, padx = 4, pady = 2)
multiple_entry.configure(state="disabled", disabledbackground="light gray")

# Generate
generate_button = tk.Button(root, text = "Generate", command = generate)
generate_button.grid(row = 17, column = 0, rowspan = 1, columnspan = 2, padx = 10, pady = 10, sticky = tk.NSEW)

# Export parameters
export_button = tk.Button(root, text = "Export parameters", command = export)
export_button.grid(row = 17, column = 2, rowspan = 1, padx = 10, pady = 10, sticky = tk.NSEW)
root.rowconfigure(17, minsize = 64)

# Progressbar
progress = tk.IntVar()
progressbar = ttk.Progressbar(root, variable = progress, maximum = 1000)
progressbar.grid(row = 18, column = 0, columnspan = 3, padx = 10, pady = 10, sticky = tk.EW)


root.mainloop()