#!/bin/sh
# MahalaOS — auto-switch PulseAudio profile for voice calls
# StateChanged signal: line1=old_state, line2=new_state, line3=reason

dbus-monitor --system "type='signal',interface='org.freedesktop.ModemManager1.Call',member='StateChanged'" 2>/dev/null | \
while read -r line; do
    case "$line" in
        *"interface=org.freedesktop.ModemManager1.Call"*)
            # New signal arriving — read the next 3 data lines
            read -r old_line
            read -r new_line
            read -r reason_line
            old_state=$(echo "$old_line" | grep -o '[0-9]*')
            new_state=$(echo "$new_line" | grep -o '[0-9]*')
            if [ "$new_state" = "4" ]; then
                pactl set-card-profile alsa_card.platform-sound "Voice Call"
            elif [ "$new_state" = "7" ] || [ "$new_state" = "6" ]; then
                pactl set-card-profile alsa_card.platform-sound "HiFi"
            fi
            ;;
    esac
done
