# remove bank/program changes, volume, pan, reverb, chorus
# and sysex from a midi file for easier importing into a daw.
# also remove any sequencer-specific events.

import argparse
import pathlib
import sys
from libmidi.types.midifile import MidiFile
from libmidi.types.messages.channel import *
from libmidi.types.messages.system import MessageSystemExclusive
from libmidi.types.messages.meta import MessageMetaSequencerSpecific
from libmidi.utils.time import *

def run():
    parser = argparse.ArgumentParser(description='Remove various events, including sys-ex and sequencer data from a midi file')
    parser.add_argument("file", help="The file to clean events from")
    parser.add_argument('-p', '--remove-pitchbends', help='Remove pitch bend events, too', action='store_true')
    parser.add_argument('-v', '--verbose', help='Print extra messages during processing', action='store_true')
    parser.add_argument('-d', '--directory', help="Output to the specified directory, instead of the current working directory")
    args = parser.parse_args()

    remove_events = [MessageProgramChange, MessageMetaSequencerSpecific, MessageSystemExclusive]
    if args.remove_pitchbends: remove_events.append(MessagePitchBend)
    status = 'with' if args.remove_pitchbends else 'without'
    remove_controlers = [0, 7, 10, 32, 91, 93, 94]

    if args.verbose: print(f'Processing {args.file} {status} pitchbend removal')
    file = pathlib.Path(args.file)
    output = pathlib.Path()
    if args.directory: output = output.joinpath(args.directory)
    output = output.joinpath(file.name)
    if output.exists(): output = pathlib.Path(output.stem + '-cn' + output.suffix)
    mid = MidiFile.from_file(file)
    start_total = sum([len(track.events) for track in mid.tracks])
    modified = 0
    for track in mid.tracks:
        track.events = list(to_abstime(track.events))
        track.events = [event for event in track.events if type(event.message) not in remove_events]
        track.events = [event for event in track.events if not (type(event.message) == MessageControlChange and event.message.control in remove_controlers)]
        track.events = list(to_reltime(track.events))
        for event in track.events:
            if hasattr(event.message, 'channel') and event.message.channel != 0:
                event.message.channel = 0
                modified += 1
        
    end_total = sum([len(track.events) for track in mid.tracks])
    removed = start_total - end_total
    mid.to_file(output)
    print(f'{file}: {removed} events removed, {modified} events modified.')
    if args.verbose: print(f'Output written to {output}.')
    print('Done!')
    input("Press enter.")
