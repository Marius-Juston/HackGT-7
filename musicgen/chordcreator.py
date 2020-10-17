from typing import List

from music21.key import Key
from music21.note import Note
from music21.stream import Stream
from music21.chord import Chord

from musicgen.rules import Rules, TriadBaroque


class ChordCreator:
    def __init__(self, inputNotes: List[Note]):
        self.inputNotes: List[Note] = inputNotes

        stream: Stream = Stream()
        for note in inputNotes:
            stream.append(note)
        self.key: Key = stream.analyze('key')

        print(
            f"Guessed key: {self.key}, Confidence: {self.key.correlationCoefficient}, Other possible keys: {self.key.alternateInterpretations}")

    def chordify(self, rules: Rules = TriadBaroque()) -> Stream:
        stream = Stream()
        prev_chord: Chord = self.first_chord()
        stream.append(prev_chord)
        for note in self.inputNotes[1:]:
            stream.append(rules.next_chord(self.key, prev_chord, note))

        return stream

    def first_chord(self) -> Chord:

        pass
