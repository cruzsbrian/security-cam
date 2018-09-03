#!/bin/sh

FILE=$1
FILEMP4="${FILE%.*}.mp4"

if [ -e $FILE ]; then
    ffmpeg -i $FILE -b:v 500K $FILEMP4 && rm $FILE
fi
