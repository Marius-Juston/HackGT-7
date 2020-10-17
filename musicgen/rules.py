from abc import ABC, abstractmethod
from music21.note import Note
from music21.chord import Chord
from music21.key import Key


class Rules(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def next_chord(self, key: Key, previous_chord: Chord, next_note: Note) -> Chord:
        pass


class TriadBaroque(Rules):
    def __init__(self):
        super().__init__()

    def next_chord(self, key: Key, previous_chord: Chord, next_note: Note) -> Chord:
        previous_rank = key.getScaleDegreeFromPitch(previous_chord.root())
        print(previous_rank)
        return Chord()
