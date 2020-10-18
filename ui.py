import os
import platform
import subprocess
from io import TextIOWrapper
from tkinter.filedialog import askopenfile, asksaveasfile

import cv2
import numpy as np
import pygubu

import musicgen
from keys import *

KEY = A_MINOR
NOTES_LIST = list(map(lambda note: note.name[0], KEY.getPitches()))
CYPHER = musicgen.rules.TriadBaroqueCypher(KEY)
min_quarter_length = .25
max_quarter_length = 2

min_vol = 20
max_vol = 127


class ImageAudioConverter:
    SPLIT_NUMBER = (16, 16)  # (rows, cols)

    def __init__(self, notes):
        self.platform = platform.system()

        # 1: Create a builder
        self.notes = notes
        self.available_notes = notes
        self.builder = builder = pygubu.Builder()

        # 2: Load an ui file
        builder.add_from_file('converter.ui')

        # 3: Create the mainwindow
        self.mainwindow = builder.get_object('mainwindow')
        self.builder.tkvariables['row_size'].set(ImageAudioConverter.SPLIT_NUMBER[0])
        self.builder.tkvariables['col_size'].set(ImageAudioConverter.SPLIT_NUMBER[1])

        builder.connect_callbacks(self)
        self.file = None

    def run(self):
        self.mainwindow.mainloop()

    def select_file(self):
        current_dir = os.getcwd()

        self.file: TextIOWrapper = askopenfile(initialdir=current_dir,
                                               filetypes=(('Images', "*.jpg;*.png"), ("Audio", "*.mid")))

        if self.file is not None:
            self.builder.tkvariables['file_location_var'].set(os.path.basename(self.file.name))

            # print(self.file.name)

    def _read_image(self, img_loc):
        return cv2.imread(img_loc)

    def convert(self):
        if self.file is not None:
            ImageAudioConverter.SPLIT_NUMBER = (
                self.builder.tkvariables['row_size'].get(), self.builder.tkvariables['col_size'].get())
            # print("rows: ", ImageAudioConverter.SPLIT_NUMBER[0], "cols: ", ImageAudioConverter.SPLIT_NUMBER[1])

            if self.file.name.endswith('jpg') or self.file.name.endswith('png'):
                self.convert_img_to_music()
            else:
                self.convert_music_to_img(self.file.name)

    def convert_img_to_music(self, cypher=CYPHER):
        if self.file is not None:
            image = self._read_image(self.file.name)
            notes, quarter_length, volume = self.split_image_transform(image)

            notes /= 255
            notes *= (len(self.available_notes) - 1)
            notes = np.rint(notes).astype(int)
            notes = np.vectorize(lambda x: self.available_notes[x])(notes)
            # print(notes.shape)

            quarter_length /= 255
            quarter_length = quarter_length * (max_quarter_length - min_quarter_length) + min_quarter_length

            quarter_length /= .25
            quarter_length = np.rint(quarter_length)
            quarter_length *= .25

            volume /= 255
            volume = volume * (max_vol - min_vol) + min_vol

            chords = musicgen.create_chords([(note, vel, vol) for note, vel, vol in zip(notes, quarter_length, volume)],
                                            cypher)

            file_types = [('Midi', '*.mid')]
            file = asksaveasfile(filetypes=file_types, defaultextension=file_types)

            if file is not None:
                chords.write("midi", file.name)
                self.open_file_in_system(file.name)

    def convert_music_to_img(self, music_in: str, cypher: musicgen.rules.Cypher = CYPHER):
        note_identifiers = musicgen.decode(music_in, cypher)
        notes = []
        quarter_lengths = []
        volumes = []
        for note_identifier in note_identifiers:
            notes.append(note_identifier[0])
            quarter_lengths.append(note_identifier[1])
            volumes.append(note_identifier[2])
        self.decode_music(np.asarray(notes), np.asarray(quarter_lengths), np.asarray(volumes))

    def decode_music(self, notes, quarter_lengths, volumes):
        notes = np.array([NOTES_LIST.index(note[0]) for note in notes])
        notes = notes / (len(NOTES_LIST) - 1)
        notes *= 255

        volumes = (volumes - min_vol) * 255 / (max_vol - min_vol)

        quarter_lengths = (quarter_lengths - min_quarter_length) * 255 / (max_quarter_length - min_quarter_length)

        shape = (ImageAudioConverter.SPLIT_NUMBER[0], ImageAudioConverter.SPLIT_NUMBER[1], 1)

        notes = notes.reshape(shape)
        quarter_lengths = quarter_lengths.reshape(shape)
        volumes = volumes.reshape(shape)

        new_image = np.concatenate((notes, quarter_lengths, volumes), axis=2)
        new_image = new_image.astype(np.uint8)

        file_types = [('PNG', "*.png"), ('JPEG', '*.jpeg')]
        file = asksaveasfile(filetypes=file_types, defaultextension=file_types)

        if file is not None:
            cv2.imwrite(file.name, new_image)
            self.open_file_in_system(file.name)

    def split_image_transform(self, image):
        note = []
        quarter_length = []
        volume = []

        d_height = image.shape[0] / ImageAudioConverter.SPLIT_NUMBER[0]
        d_width = image.shape[1] / ImageAudioConverter.SPLIT_NUMBER[1]

        ratio_h = np.floor(d_height) * ImageAudioConverter.SPLIT_NUMBER[0]
        ratio_w = np.floor(d_width) * ImageAudioConverter.SPLIT_NUMBER[1]

        image = cv2.resize(image, (int(ratio_w), int(ratio_h)))

        d_height = int(image.shape[0] / ImageAudioConverter.SPLIT_NUMBER[0])
        d_width = int(image.shape[1] / ImageAudioConverter.SPLIT_NUMBER[1])

        for r in range(0, image.shape[0], d_height):
            for c in range(0, image.shape[1], d_width):
                crop = image[r:r + d_height, c:c + d_width]

                note.append(np.median(crop[:, :, 0]))
                quarter_length.append(np.median(crop[:, :, 1]))
                volume.append(np.median(crop[:, :, 2]))

        return np.array(note), np.array(quarter_length), np.array(volume)

    def open_file_in_system(self, file):
        if self.platform == 'Darwin':  # macOS
            subprocess.call(('open', file))
        elif self.platform == 'Windows':  # Windows
            os.startfile(file)
        else:  # linux variants
            subprocess.call(('xdg-open', file))


if __name__ == '__main__':
    app = ImageAudioConverter(NOTES_LIST)
    app.run()
