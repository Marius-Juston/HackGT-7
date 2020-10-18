from typing import List

from music21.chord import Chord
from music21.key import Key
from music21.note import Note
from music21.stream import Stream

from musicgen.rules import Rules, TriadBaroque


class ChordCreator:
    def __init__(self, input_notes: List[Note]):
        """
        ChordCreator is a utility class that can supply a Rules instance with a key and notes to create chords out of.

        :param input_notes: A list of music21.note.Note objects. Chords get fitted to these Notes.
        """
        self.inputNotes: List[Note] = input_notes

        self.inputStream: Stream = Stream()
        for note in input_notes:
            self.inputStream.append(note)
        self.key: Key = self.inputStream.analyze('key')

        # print(
        #     f"Guessed key: {self.key}, Confidence: {self.key.correlationCoefficient}, Other possible keys: {self.key.alternateInterpretations}")

    def chordify(self, rules: Rules = TriadBaroque()) -> Stream:
        """
        Run the process that creates the Chords. Chords are determined completely by a Rules object.
        :param rules: A Rules object that determines how the Chords are fitted. Defaults to a Rules object that
        generates triads based on the rules from the Baroque period.
        :return: A flat music21.stream.Stream that contains the Chords.
        """
        stream = Stream()
        prev_chord: Chord = rules.first_chord(self.key, self.inputNotes[0])
        stream.append(prev_chord)
        for note in self.inputNotes[1:]:
            prev_chord = rules.next_chord(self.key, prev_chord, note)
            stream.append(prev_chord)
        stream.append(rules.end_cadence(self.key, prev_chord))

        return stream.flat
