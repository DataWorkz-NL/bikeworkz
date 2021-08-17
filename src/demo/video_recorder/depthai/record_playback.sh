# Record.
python depthai_demo.py -v ./video.h264 -s previewout

# Convert.
ffmpeg -r 30 -i ./video.h264 ./video.mp4
