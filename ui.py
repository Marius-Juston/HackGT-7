import os
from io import TextIOWrapper
from tkinter.filedialog import askopenfile

import cv2
import numpy as np
import pygubu
import skimage.measure

import musicgen
from music21.key import Key

NOTES_LIST = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
CYPHER = musicgen.rules.TriadBaroqueCypher(Key("a"))
min_quater_length = .25
max_quater_length = 2


# C:\Users\mariu\Anaconda3\envs\HackGT-7\Scripts\pygubu-designer.exe

class ImageAudioConverter:
    KERNEL = {"kernel_size": (4, 4, 3), "kernel_type": np.median}
    CHORD_LENGTH = 20
    SPLIT_NUMBER = (16, 16)  # (rows, cols)

    def __init__(self, notes):
        # 1: Create a builder
        self.notes = notes
        self.available_notes = notes
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

        self.builder.tkvariables['file_location_var'].set(os.path.basename(self.file.name))

        print(self.file.name)

    def _read_image(self, img_loc):
        return cv2.imread(img_loc)

    def kernel_image_transform(self, image):
        return skimage.measure.block_reduce(image, ImageAudioConverter.KERNEL['kernel_size'],
                                            ImageAudioConverter.KERNEL['kernel_type'])

    def convert_img_to_music(self, transform_type='split', cypher=CYPHER):
        if self.file is not None:
            image = self._read_image(self.file.name)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)

            if transform_type == 'kernel':
                notes = self.kernel_image_transform(image)
            else:
                notes, quarter_length, volume = self.split_image_transform(image)

            notes /= 255
            notes *= (len(self.available_notes) - 1)
            notes = np.rint(notes).astype(int)
            notes = np.vectorize(lambda x: self.available_notes[x])(notes)

            # avg: 0.5 min: 0.25 3
            # .25 2

            quarter_length /= 255
            quarter_length = quarter_length * (max_quater_length - min_quater_length) + min_quater_length

            quarter_length /= .25
            quarter_length = np.rint(quarter_length)
            quarter_length *= .25

            volume /= 255
            volume *= 127

            chords = musicgen.create_chords([(note, vel, vol) for note, vel, vol in zip(notes, quarter_length, volume)], cypher)
            chords.write("midi", "from_img.mid")
            chords.write("xml", "from_img.xml")

        # print("Convert")

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
        notes = np.array([NOTES_LIST.index(note) for note in notes])
        notes = notes / (len(NOTES_LIST) - 1)
        notes *= 255

        volumes /= 127
        volumes *= 255

        quarter_lengths = (quarter_lengths - min_quater_length) * 255 / (max_quater_length - min_quater_length)

        shape = (ImageAudioConverter.SPLIT_NUMBER[0], ImageAudioConverter.SPLIT_NUMBER[1], 1)

        notes = notes.reshape(shape)
        quarter_lengths = quarter_lengths.reshape(shape)
        volumes = volumes.reshape(shape)

        new_image = np.concatenate((notes, quarter_lengths, volumes), axis=2)
        new_image = new_image.astype(np.uint8)

        cv2.imwrite("ouput.png", cv2.cvtColor(new_image, cv2.COLOR_HLS2BGR))

        print(new_image)

    def play_music(self):
        print("Play music")

    def validate_location(self):
        print("Hello")

    def split_image_transform(self, image):
        note = []
        quater_length = []
        volume = []

        d_height = image.shape[0] / ImageAudioConverter.SPLIT_NUMBER[0]
        d_width = image.shape[1] / ImageAudioConverter.SPLIT_NUMBER[1]

        ratio_h = np.floor(d_height) * ImageAudioConverter.SPLIT_NUMBER[0]
        ratio_w = np.floor(d_width) * ImageAudioConverter.SPLIT_NUMBER[0]

        image = cv2.resize(image, (int(ratio_h), int(ratio_w)))

        d_height = int(image.shape[0] / ImageAudioConverter.SPLIT_NUMBER[0])
        d_width = int(image.shape[1] / ImageAudioConverter.SPLIT_NUMBER[1])

        for r in range(0, image.shape[0], d_height):
            for c in range(0, image.shape[1], d_width):
                crop = image[r:r + d_height, c:c + d_width]

                note.append(np.median(crop[:, :, 0]))
                quater_length.append(np.median(crop[:, :, 1]))
                volume.append(np.median(crop[:, :, 2]))

        return np.array(note), np.array(quater_length), np.array(volume)


if __name__ == '__main__':
    app = ImageAudioConverter(NOTES_LIST)


    class Test:
        def __init__(self):
            self.name = 'images/Mona_Lisa.jpg'


    app.file = Test()
    # app.convert(transform_type='split')
    app.convert_img_to_music()
    app.convert_music_to_img('from_img.mid')

    # app.run()
