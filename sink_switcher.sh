#!/bin/bash

# 1. Get the current default sink ID (numerical only)
CURRENT_SINK=$(wpctl inspect @DEFAULT_SINK@ | grep -m 1 "id" | awk '{print $2}' | tr -d ',')

# 2. Get the IDs for your specific devices
ID_SHURE=$(wpctl status | grep "Shure MV7 Analog Stereo" | grep -oP '\d+(?=\.)' | head -n 1)
ID_DAC=$(wpctl status | grep "PCM2704 16-bit stereo audio DAC Digital Stereo" | grep -oP '\d+(?=\.)' | head -n 1)

# 3. Toggle Logic
if [ "$CURRENT_SINK" == "$ID_SHURE" ]; then
    wpctl set-default "$ID_DAC"
    notify-send "Audio Output" "Switched to: DAC (PCM2704)" --icon=audio-speakers
else
    wpctl set-default "$ID_SHURE"
    notify-send "Audio Output" "Switched to: Shure MV7" --icon=audio-card
fi