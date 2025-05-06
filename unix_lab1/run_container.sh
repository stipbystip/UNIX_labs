#!/bin/sh

if [ -z "$1" ]; then
    echo "Input number of containers. For example: ./run_container.sh 10"
    exit 1
fi

COUNT=$1

for i in $(seq 1 "$COUNT"); do
    docker run -d --rm -v unix_lab2:/data lab2_unixx
done