import os
from io import TextIOWrapper
from tkinter.filedialog import askopenfile

import cv2
import numpy as np
import pygubu
import skimage.measure

NOTES_LIST = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


# C:\Users\mariu\Anaconda3\envs\HackGT-7\Scripts\pygubu-designer.exe

class ImageAudioConverter:
    KERNEL = {"kernel_size": (4, 4, 3), "kernel_type": np.median}
    chord_length = 20

    def __init__(self, notes):
        # 1: Create a builder
        self.notes = notes
        self.avaliable_notes = notes
        self.builder = builder = pygubu.Builder()

        # 2: Load an ui file
        builder.add_from_file('converter.ui')

        # 3: Create the mainwindow
        self.mainwindow = builder.get_object('mainwindow')

        builder.connect_callbacks(self)
        self.file = None

    def run(self):
        self.mainwindow.mainloop()

    def select_file(self):
        current_dir = os.getcwd()

        self.file: TextIOWrapper = askopenfile(initialdir=current_dir, filetypes=(('jpef', "*.jpg"), ("png", "*.png")))

        print(self.file.name)

    def _read_image(self, img_loc):
        return cv2.imread(img_loc)

    def convert(self):
        if self.file is not None:
            image = self._read_image(self.file.name)

            reduced_image = skimage.measure.block_reduce(image, ImageAudioConverter.KERNEL['kernel_size'],
                                                         ImageAudioConverter.KERNEL['kernel_type'])

            min_v = reduced_image.min()
            max_v = reduced_image.max()
            notes: np.ndarray = reduced_image.flatten()
            notes = (notes - min_v) / (max_v - min_v)
            notes *= (len(self.avaliable_notes) - 1)
            notes = np.rint(notes).astype(int)
            notes = np.vectorize(lambda x: self.avaliable_notes[x])(notes)
            notes = notes.reshape((-1, ImageAudioConverter.chord_length))

        print("Convert")

    def play_music(self):
        print("Play music")

    def validate_location(self):
        print("Hello")


if __name__ == '__main__':
    app = ImageAudioConverter()
    app.run()
