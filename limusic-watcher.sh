#!/usr/bin/env bash

SCRIPT_PATH="$HOME/projects/steelseries-audio/steelseries-audio"

# ANSI Colors
C_CYAN="\033[36m"
C_BOLD="\033[1m"
C_GREEN="\033[32m"
C_RESET="\033[0m"

echo -e "${C_CYAN}${C_BOLD}Launching Native Arch playerctl MPRIS Tracking Daemon...${C_RESET}"
echo "Listening for limusic track changes..."

# Follow the artist metadata stream natively across D-Bus
playerctl --player=limusic metadata --format '{{ artist }}' --follow | while read -r artist; do
    # Skip empty lines
    if [ -z "$artist" ]; then
        continue
    fi

    # Convert to lowercase for loose keyword evaluation
    artist_lower=$(echo "$artist" | tr '[:upper:]' '[:lower:]')
    profile="audiophile"

    # Match rules mapping strings to your ssaudio profiles
    if [[ "$artist_lower" =~ (animals as leaders|periphery|the contortionist|dance gavin dance|thank you scientist) ]]; then
        profile="math-metal"
    elif [[ "$artist_lower" =~ (mastodon|rainbows are free) ]]; then
        profile="sludge-prog"
    elif [[ "$artist_lower" =~ (freddie dredd|pouya|baker ya maker|devilish trio|1nonly|lilbubblegum|father|zack fox|"$uicideboi$"|ghostemane|"fukkit & dutchman") ]]; then
        profile="phonk-rap"
    elif [[ "$artist_lower" =~ (baiyon|boys noize|justice|mstrkrft) ]]; then
        profile="electro-synth"
    elif [[ "$artist_lower" =~ (above the law|prince paul|shoestring|stetsasonic|indo g|jonzun crew|de la soul|naughty by nature) ]]; then
        profile="kung-faux"
    fi

    echo -e "${C_CYAN}[MPRIS Sync]${C_RESET} Track Changed -> Artist: ${C_BOLD}${artist}${C_RESET} -> Profile: ${C_GREEN}${profile}${C_RESET}"

    # Execute your friend's core equalizer tool profile command
    "$SCRIPT_PATH" profile "$profile"
done
