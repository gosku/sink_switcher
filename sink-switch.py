#!/usr/bin/env python3
# this little script switches the sound sink on ubuntu
# https://askubuntu.com/questions/156895/how-to-switch-sound-output-with-key-shortcut/1203350#1203350 and https://askubuntu.com/questions/1011806/how-do-i-switch-the-audio-outputs-of-an-audio-device-from-cli?noredirect=1&lq=1 were helpful
import argparse
import re
import subprocess
from typing import List


class Sink:
    """
    A simple representation of all relevant info of an audio sink for this script
    """

    def __init__(self, index, name, state):
        self.index = index
        self.name = name
        self.state = state
        if state in ["RUNNING", "IDLE"]:
            self.selected = True
        else:
            self.selected = False

    def __str__(self):
        return 'sink\nindex: {self.index}\nname: {self.name}\nstate: {self.state}\nselected: {self.selected}\n'.format(self=self)


class Sink_Input:
    """
    A simple representation of all relevant info of an audio sink-input for this script
    """

    def __init__(self, index, application_name, sink, state):
        self.index = index
        self.application_name = application_name
        self.sink = sink
        self.state = state

    def __str__(self):
        return 'sink-input\nindex: {self.index}\napplication_name: {self.application_name}\nsink: {self.sink}\nstate: {self.state}\n'.format(self=self)


def get_sinks() -> List[Sink]:
    pacmd_output = str(subprocess.check_output(["pacmd", "list-sinks"]))
    sinks_raw = pacmd_output.split("index: ")
    sinks = []
    for sink_raw in sinks_raw[1:]:
        index = int(re.findall(r"^\d+", sink_raw)[0])
        name = re.findall("device.description = \"[^\"]*\"", sink_raw)[0][22:-1]
        state = re.findall("state: [A-Z]*", sink_raw)[0][7:]
        sink = Sink(index, name, state)
        sinks.append(sink)
    return sinks


def get_sink_inputs() -> List[Sink_Input]:
    sink_inputs = []
    pacmd_output = str(subprocess.check_output(["pacmd", "list-sink-inputs"]))
    inputs_raw = pacmd_output.split("index: ")
    for input_raw in inputs_raw[1:]:
        index = int(re.findall(r"^\d+", input_raw)[0])
        sink = int(re.findall(r"sink: \d*", input_raw)[0][5:])
        application_name = re.findall("application.name = \"[^\"]*\"", input_raw)[0][20:-1]
        state = re.findall("state: [A-Z]*", input_raw)[0][7:]
        sink_input = Sink_Input(index, application_name, sink, state)
        sink_inputs.append(sink_input)
    return sink_inputs


def switch_to_next_sink(sinks: List[Sink], notify: bool) -> None:
    next_sink = sinks[0]
    for i in range(len(sinks)):
        if sinks[i].selected:
            if i == len(sinks) - 1:
                next_sink = sinks[0]
            else:
                next_sink = sinks[i + 1]
    switch_to_sink(sink=next_sink, notify=notify)


def switch_to_sink_with_name(sinks: List[Sink], notify: bool, device_name: str) -> None:
    """
    Switch default sink to the first sink that matches the given device_name

    If notify is True and no matches are found, the function notifies about it
    """
    for sink in sinks:
        if hasattr(sink, "name"):
            if sink.name.find(device_name) != -1:
                switch_to_sink(sink=sink, notify=notify)
                return
    if notify:
        subprocess.call(["notify-send", f"No device found with name {device_name}"])


def switch_to_sink(sink: Sink, notify: bool) -> None:
    """
    Switch default sink to the given sink and make all the applications to use it

    If notify is True, the function will try to send a notification
    """
    subprocess.call(["pacmd", "set-default-sink", str(sink.index)])
    # move all apps to next sink
    for sink_input in get_sink_inputs():
        subprocess.call(["pacmd", "move-sink-input", str(sink_input.index), str(sink.index)])
    if notify:
        subprocess.call(["notify-send", "Changed audio sink", "new audio sink is " + sink.name])


def main() -> None:
    parser = argparse.ArgumentParser(description=("""
        Switches to the 'next' audio sink on Ubuntu and can provide additional
        info on sound sinks.
        If no arguments are passed only the next audio sink is selected.
        """))
    parser.add_argument('-l', '--list',
                        help='List all the pacmd list-sinks and list-sink-inputs', action='store_true')
    parser.add_argument('-m', '--match',
                        help='Activate first sink that matches the given name', type=str)

    parser.add_argument('-n', '--notify', help='Send notification to the desktop', action='store_true')

    args = parser.parse_args()

    sinks = get_sinks()
    if args.state:
        for sink in sinks:
            print(sink)
        sink_inputs = get_sink_inputs()
        for sink_input in sink_inputs:
            print(sink_input)
    elif args.match:
        switch_to_sink_with_name(sinks=sinks, device_name=args.match, notify=args.notify)
    else:
        switch_to_next_sink(sinks, args.notify)


main()
