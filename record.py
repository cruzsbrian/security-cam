#!/usr/bin/env python2

import numpy as np
import cv2

import time
import subprocess

FRAME_COMPARISON_DELAY = 10 # frames to skip when comparing to test for motion
MOVEMENT_THRESHOLD = 40 # higher = less sensitive to motion
POST_MOTION_DELAY = 5 # seconds
PRE_MOTION_FRAMES = 60 # number of frames to include from before motion starts
DIFF_BLUR = 31 # must be an odd number of pixels

# open the first video in
cap = cv2.VideoCapture(0)

# video encoding
fourcc = cv2.cv.CV_FOURCC(*'mp4v')
out = None
lastFilename = None

# font used for drawing text on the image
font = cv2.FONT_HERSHEY_SIMPLEX

lastFrame = None
count = 0

lastMotionTime = 0

buff = []

moving = False
filming = False

while cap.isOpened():
    ret, frame = cap.read()

    # if a frame was returned
    if ret:

        # motion detection
        if count == 0:
            # lastFrame will be None the first time
            if lastFrame is not None:
                # take the difference between the two images and blur it
                diff = cv2.subtract(frame, lastFrame)
                diff = cv2.GaussianBlur(diff, (DIFF_BLUR, DIFF_BLUR), 0)

                # threshold the blurred difference, so that only large changes
                # are left
                ret, diff = cv2.threshold(diff, MOVEMENT_THRESHOLD, 255,
                        cv2.THRESH_BINARY)

                # a nonzero diff image after the threshold means there is
                # movement
                diffIntensity = np.sum(diff)
                moving = diffIntensity > 0

                # record the time of the movement
                if moving:
                    lastMotionTime = time.time()

            lastFrame = frame.copy()

        # make sure count == 0 every FRAME_COMPARISON_DELAY frames
        count += 1
        if count == FRAME_COMPARISON_DELAY:
            count = 0

        # get the timestamp in YYYY-MM-DD hour:minute:second format
        timestamp = time.strftime('%Y-%m-%d_%H:%M:%S')

        # draw the timestamp first with thick black text then with thin white
        # text. this will make it legible on any background
        cv2.putText(frame, timestamp, (10, 20), font, 0.75, (0, 0, 0), 2)
        cv2.putText(frame, timestamp, (10, 20), font, 0.75, (255, 255, 255))

        # start filming with a new output file once motion starts
        if moving and not filming:
            out = cv2.VideoWriter(timestamp + '.mov', fourcc, 30, (640, 480))
            lastFilename = timestamp

            # write the frames from the buffer
            # in order from oldest to newest
            while len(buff) > 0:
                out.write(buff.pop(0))

            filming = True

        if filming:
            out.write(frame)

            # display recording status for the live view
            cv2.putText(frame, 'REC', (580, 20), font, 0.75, (0, 0, 255), 2)

            if time.time() - lastMotionTime > POST_MOTION_DELAY:
                # stop filming and release the videowriter
                filming = False
                out.release()

                # convert the .mov to a .mp4 with ffmpeg for web display and
                # file size. then delete the .mov
                subprocess.Popen(['ffmpeg', '-i', lastFilename + '.mov',
                    lastFilename + '.mp4'])

        else:
            # add frame to the buffer
            buff.append(frame)

            # make sure buffer is not longer and PRE_MOTION_FRAMES
            # discard oldest frames first
            while len(buff) > PRE_MOTION_FRAMES:
                buff.pop(0)

        # display the live view
        cv2.imshow('frame', frame)

        # wait 1ms for q key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    else:
        # if no frame was returned from cap, break the loop
        break

if out is not None:
    out.release()

cap.release()
cv2.destroyAllWindows()
