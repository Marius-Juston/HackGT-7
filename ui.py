from tkinter.filedialog import askopenfile

import pygubu


# C:\Users\mariu\Anaconda3\envs\HackGT-7\Scripts\pygubu-designer.exe

class ImageAudioConverter:

    def __init__(self):
        # 1: Create a builder
        self.builder = builder = pygubu.Builder()

        # 2: Load an ui file
        builder.add_from_file('converter.ui')

        # 3: Create the mainwindow
        self.mainwindow = builder.get_object('mainwindow')

        builder.connect_callbacks(self)

    def run(self):
        self.mainwindow.mainloop()

    def select_file(self):
        file = askopenfile()

    def convert(self):
        print("Convert")

    def play_music(self):
        print("Play music")

    def validate_location(self):
        print("Hello")


if __name__ == '__main__':
    app = ImageAudioConverter()
    app.run()
