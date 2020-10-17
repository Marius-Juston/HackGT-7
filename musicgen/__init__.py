from typing import List, Tuple, Union

from music21.note import Note
from music21.stream import Stream

from musicgen.chordcreator import ChordCreator


def create_chords(notes_in: List[Tuple[str, Union[float, int]]]) -> Stream:
    notes_out: List[Note] = []
    for note in notes_in:
        note_out = Note(note[0])
        note_out.quarterLength = note[1]
        notes_out.append(note_out)

    chord_creator = ChordCreator(notes_out)
    # chord_creator.inputStream.show()
    # chord_creator.chordify().show()
    return chord_creator.chordify()


if __name__ == '__main__':
    # os.environ['musicxmlPath'] = r'L:\Program Files\MuseScore 3\bin\MuseScore3.exe'
    create_chords([("B", 1), ("F", 1), ("A", 1), ("G", 1), ("D", 1), ("C", 1), ("B", 1), ("E", 1)]).show()
