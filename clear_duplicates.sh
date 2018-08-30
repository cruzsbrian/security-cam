for FILE in `ls *.mp4`; do
    FILEMOV="${FILE%%.*}.mov"
    if [ -e $FILEMOV ]; then
        rm $FILEMOV
    fi
done
