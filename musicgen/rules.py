from abc import ABC, abstractmethod
from typing import List, Dict

from music21.chord import Chord
from music21.key import Key
from music21.note import Note
from music21.stream import Stream


class Rules(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def next_chord(self, key: Key, previous_chord: Chord, next_note: Note) -> Chord:
        pass

    @abstractmethod
    def first_chord(self, key: Key, note: Note) -> Chord:
        pass

    @abstractmethod
    def end_cadence(self, key: Key, previous_chord: Chord) -> Stream:
        pass

    @staticmethod
    def build_chord(bass: Note, intervals: List[str]):
        chord = Chord([bass])
        previous = bass
        for interval in intervals:
            previous = previous.transpose(interval)
            chord.add([previous])
        return chord

    @staticmethod
    def build_major_triad(bass: Note) -> Chord:
        return Rules.build_chord(bass, ["M3", "m3"])

    @staticmethod
    def build_minor_triad(bass: Note) -> Chord:
        return Rules.build_chord(bass, ["m3", "M3"])

    @staticmethod
    def build_diminished_triad(bass: Note) -> Chord:
        return Rules.build_chord(bass, ["m3", "m3"])

    @staticmethod
    def build_augmented_triad(bass: Note) -> Chord:
        return Rules.build_chord(bass, ["M3", "M3"])


class TriadBaroque(Rules):
    def __init__(self):
        """
        This Rules object will generate Chords based on the chord progression rules in place in the Baroque Era of
        music. The original note isn't preserved in any identifiable way.
        """
        super().__init__()
        self.chord_degrees = [
            [1, 3, 5],
            [2, 4, 6],
            [3, 5, 7],
            [4, 6, 1],
            [5, 7, 2],
            [6, 1, 3],
            [7, 2, 4],
        ]
        self.next_degree: List[List[int]] = [
            [5, 6, 4, 1, 2, 7, 3],  # 1 2 3 4 5 6 7
            [5, 4, 7, 2, 1],  # 1 2 3 5 5 6 7
            [6, 1, 4, 2, 5, 3],  # 1 2 3 4 5 6 7
            [5, 2, 7, 1, 4],  # 1 2 3 4 5 6 7
            [1, 5, 6, 4, 2, 7],  # 1 2 3 4 5 6 7
            [4, 2, 6, 1, 5],  # 1 2 3 4 5 6 7
            [1, 5, 7, 6, 2, 4]  # 1 2 3 4 5 6 7
        ]
        self.types: Dict[str, Dict[str, List[int]]] = {
            "major": {
                "major": [1, 4, 5],
                "minor": [2, 3, 6],
                "diminished": [7]
            },
            "minor": {
                "major": [2, 3, 5, 6],
                "minor": [1, 4],
                "diminished": [7]
            }
        }
        self.end_cadence_preferences = [
            [5, 1],
            [5, 6],
            [6, 4, 1],
            [5, 1],
            [5, 1],
            [4, 1],
            [1]
        ]

    def next_chord(self, key: Key, previous_chord: Chord, next_note: Note) -> Chord:
        # Proceed, preferring motion to anything other than 3/7 over static
        previous_degree = key.getScaleDegreeFromPitch(previous_chord.root())
        adjusted_next_note = next_note
        adjusted_next_note.pitch.accidental = key.accidentalByStep(adjusted_next_note.pitch.step)
        next_note_degree = key.getScaleDegreeFromPitch(adjusted_next_note)
        next_chord_possibilities = self.next_degree[previous_degree - 1]
        next_degree = -1
        hold = -1
        for chord_possibility in next_chord_possibilities:
            if next_note_degree in self.chord_degrees[chord_possibility - 1] and not (
                    key.mode == "minor" and chord_possibility == 7):
                if chord_possibility == previous_degree:
                    hold = chord_possibility
                else:
                    next_degree = chord_possibility
                    break

        if next_degree in [-1, 3, 7] and hold != -1:
            next_degree = hold

        chord_builder = lambda x: Chord(x)
        if next_degree in self.types[key.mode]["major"]:
            chord_builder = self.build_major_triad
        elif next_degree in self.types[key.mode]["minor"]:
            chord_builder = self.build_minor_triad
        elif next_degree in self.types[key.mode]["diminished"]:
            chord_builder = self.build_diminished_triad

        # print(next_note, next_degree, chord_builder(key.pitchFromDegree(next_degree)))
        chord = chord_builder(key.pitchFromDegree(next_degree))
        chord.quarterLength = next_note.quarterLength
        chord.volume = next_note.volume


        return chord

    def first_chord(self, key: Key, note: Note) -> Chord:
        # Take preference for I, then go to V, IV, and II
        tonic = key.tonic
        bass = tonic
        chord_builder = self.build_major_triad
        degree = key.getScaleDegreeFromPitch(note)
        if degree in self.chord_degrees[0]:
            bass = tonic
            if key.mode == "minor":
                chord_builder = self.build_minor_triad
        elif degree in self.chord_degrees[4]:
            bass = tonic.transpose("P5")
        elif degree in self.chord_degrees[3]:
            bass = tonic.transpose("P4")
            if key.mode == "minor":
                chord_builder = self.build_minor_triad
        elif degree in self.chord_degrees[1]:
            bass = tonic.transpose("M2")
            if key.mode == "major":
                chord_builder = self.build_major_triad

        chord = chord_builder(bass)
        chord.quarterLength = note.quarterLength
        chord.volume = note.volume

        return chord

    def end_cadence(self, key: Key, previous_chord: Chord) -> Stream:
        # Cadence preference: 1-5-1, 2-5-6, 3-6-4-1, 4-5-1, 5-5-1, 6-4-1, 7-1
        previous_degree = key.getScaleDegreeFromPitch(previous_chord.root())
        next_chords = self.end_cadence_preferences[previous_degree - 1]
        out = Stream()
        for chord_degree in next_chords:
            chord_builder = lambda x: Chord(x)
            if chord_degree in self.types[key.mode]["major"]:
                chord_builder = self.build_major_triad
            elif chord_degree in self.types[key.mode]["minor"]:
                chord_builder = self.build_minor_triad
            elif chord_degree in self.types[key.mode]["diminished"]:
                chord_builder = self.build_diminished_triad
            chord = chord_builder(key.pitchFromDegree(chord_degree))
            chord.quarterLength = 2
            out.append(chord)

        return out


class TriadBaroqueCypher(TriadBaroque):
    def __init__(self, secret_key: Key):
        """
        Functionally the same to the TriadBaroque Rules, with the only exception being that the input note is the bass
        of the chord. This chord creation is reversible. The cadence doesn't encode information and is used to make the
        music sound better.
        :param secret_key: The Key that the chords will fit to. This is to make sure the encoding process is reversible.
        """
        super().__init__()
        self.secret_key = secret_key

    def next_chord(self, key: Key, previous_chord: Chord, next_note: Note) -> Chord:
        chord = super().next_chord(self.secret_key, previous_chord, next_note)

        index = 0
        for note in chord.notes:
            if note.name[0] == next_note.name[0]:
                break
            index += 1

        chord.inversion(index)

        return chord

    def first_chord(self, key: Key, note: Note) -> Chord:
        chord = super().first_chord(self.secret_key, note)

        index = 0
        for chord_note in chord.notes:
            if chord_note.name[0] == note.name[0]:
                break
            index += 1

        return chord

    def end_cadence(self, key: Key, previous_chord: Chord) -> Stream:
        return super().end_cadence(self.secret_key, previous_chord)

    def reverse(self, input_stream: Stream) -> List[Note]:
        pass
