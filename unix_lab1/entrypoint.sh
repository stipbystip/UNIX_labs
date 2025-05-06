#!/bin/sh

# Create unique id for container
CONTAINER_ID=$(cat /proc/sys/kernel/random/uuid)
COUNTER=1

DATA_DIR="/data"
LOCK_FILE="$DATA_DIR/.lockfile"

echo "Starting container with ID $CONTAINER_ID"

while true; do
    flock "$LOCK_FILE" sh -c '
        for i in $(seq -w 1 999); do
            FILE='"$DATA_DIR"'/'"$i"'
            if [ ! -e "$FILE" ]; then
                echo "'"$CONTAINER_ID"' '"$COUNTER"'" > "$FILE"
                break
            fi
        done
    '
    echo "Sleep 1 second"
    sleep 1

    for i in $(seq -w 1 999); do
        FILE="$DATA_DIR/$i"
        if [ -f "$FILE" ] && grep -q "$CONTAINER_ID $COUNTER" "$FILE"; then
            rm -f "$FILE"
            break
        fi
    done

    COUNTER=$((COUNTER + 1))
    sleep 1
done