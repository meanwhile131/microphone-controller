notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
note_count = len(notes)
octave_count = 10
octaves = list(range(octave_count))

base_f = 440  # ISO 16:1975
base_octave = 4
base_note = 4 * note_count + notes.index("A")

note_to_freq = [{notes[note]: base_f * 2 ** ((octave * note_count + note - base_note) / note_count)
                 for note in range(note_count)} for octave in octaves]
