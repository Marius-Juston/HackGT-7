from typing import List

from music21.key import Key
from music21.note import Note
from music21.stream import Stream
from music21.chord import Chord

from musicgen.rules import Rules, TriadBaroque


class ChordCreator:
    def __init__(self, inputNotes: List[Note]):
        self.inputNotes: List[Note] = inputNotes

        self.inputStream: Stream = Stream()
        for note in inputNotes:
            self.inputStream.append(note)
        self.key: Key = self.inputStream.analyze('key')

        print(
            f"Guessed key: {self.key}, Confidence: {self.key.correlationCoefficient}, Other possible keys: {self.key.alternateInterpretations}")

    def chordify(self, rules: Rules = TriadBaroque()) -> Stream:
        stream = Stream()
        prev_chord: Chord = rules.first_chord(self.key, self.inputNotes[0])
        stream.append(prev_chord)
        for note in self.inputNotes[1:]:
            prev_chord = rules.next_chord(self.key, prev_chord, note)
            stream.append(prev_chord)
        stream.append(rules.end_cadence(self.key, prev_chord))

        return stream.flat
