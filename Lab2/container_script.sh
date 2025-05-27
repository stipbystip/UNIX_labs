#!/bin/bash

SHARED_DIR="/shared_data"
LOCK_FILE="$SHARED_DIR/.lockfile"
CONTAINER_ID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1)
COUNTER=1

mkdir -p "$SHARED_DIR"

create_and_write_file() {
    (
        flock -x 200  


        for i in $(seq -w 1 999); do
            if [ ! -f "$SHARED_DIR/$i" ]; then

                echo "Container: $CONTAINER_ID, File number: $COUNTER" > "$SHARED_DIR/$i"
                echo "$i"  
                return 0
            fi
        done
        return 1  
    ) 200>"$LOCK_FILE"
}

while true; do
    if FILE_NAME=$(create_and_write_file); then
        COUNTER=$((COUNTER + 1))
        sleep 1  


        (
            flock -x 200
            rm -f "$SHARED_DIR/$FILE_NAME"
        ) 200>"$LOCK_FILE"
    else
        echo "No available file names (001-999 are occupied)"
    fi

    sleep 1  
done