from pathlib import Path
import numpy as np
import cv2      # opencv - display the video stream
import depthai  # access the camera and its data packets
import json
from collections import deque

# def running_mean(x, n):
#     cumsum = np.cumsum(np.insert(x, 0, 0)) 
#     return (cumsum[n:] - cumsum[:-n]) / float(n)

# list with 10 images
# each time, pop

# d(t=0) - d(t-1)

# Calculate average speed per pixel:
# After 2 frames we can caluclate the avg speed

CUM_FRAMES = 5
speed_list = deque(maxlen=CUM_FRAMES)

def calc_speed(f1, f0):
    return np.abs(f1 - f0)


def calc_avg_speed(l):
    cum = np.zeros_like(l[0])
    for ll in l:
        cum += ll
    return cum / len(l)


device = depthai.Device('', False)

config={'streams': ['previewout','metaout','depth'],
        'ai': {"blob_file":        str(Path('../models/mobilenet-ssd/mobilenet-ssd.blob').resolve().absolute()),
               "blob_file_config": str(Path('../models/mobilenet-ssd/mobilenet-ssd.json').resolve().absolute()),
               "calc_dist_to_bb": True,
               "camera_input": "right"}
        }
# Create the pipeline using the 'previewout, metaout & depth' stream, establishing the first connection to the device.
pipeline = device.create_pipeline(config=config)

# Retrieve model class labels from model config file.
model_config_file = config["ai"]["blob_file_config"]
mcf = open(model_config_file)
model_config_dict = json.load(mcf)
labels = model_config_dict["mappings"]["labels"]
print(labels)

if pipeline is None:   
    raise RuntimeError('Pipeline creation failed!')

nn2depth = device.get_nn_to_depth_bbox_mapping()

def nn_to_depth_coord(x, y, nn2depth):
    x_depth = int(nn2depth['off_x'] + x * nn2depth['max_w'])
    y_depth = int(nn2depth['off_y'] + y * nn2depth['max_h'])
    return x_depth, y_depth

detections = []

disparity_confidence_threshold = 130

def on_trackbar_change(value):
    device.send_disparity_confidence_threshold(value)
    return

stream_windows = ['depth']

for stream in stream_windows:
    if stream in ["disparity", "disparity_color", "depth"]:
        cv2.namedWindow(stream)
        trackbar_name = 'Disparity confidence'
        conf_thr_slider_min = 0
        conf_thr_slider_max = 255
        cv2.createTrackbar(trackbar_name, stream, conf_thr_slider_min, conf_thr_slider_max, on_trackbar_change)
        cv2.setTrackbarPos(trackbar_name, stream, disparity_confidence_threshold)

wh = 300
previous_frame = None
current_frame = None

while True:    # Retrieve data packets from the device.   # A data packet contains the video frame data.    
    nnet_packets, data_packets = pipeline.get_available_nnet_and_data_packets()

    for nnet_packet in nnet_packets:
        detections = list(nnet_packet.getDetectedObjects())

    for packet in data_packets:

        if packet.stream_name == 'depth':
            window_name = packet.stream_name
            current_frame = packet.getData()  


            if previous_frame is not None:
                speed_frame = calc_speed(current_frame, previous_frame)
                speed_list.append(speed_frame)
                avg_speed = calc_avg_speed(speed_list)

                show_frame = np.abs(speed_frame - avg_speed)
            else:
                show_frame = np.zeros_like(current_frame)

            show_frame = (65535 // show_frame).astype(np.uint8)

            previous_frame = current_frame
            # Add new frame to collection

            show_frame = cv2.applyColorMap(show_frame, cv2.COLORMAP_HOT)
            cv2.imshow(window_name, show_frame)

    if cv2.waitKey(1) == ord('q'):
        break

# The pipeline object should be deleted after exiting the loop. Otherwise device will continue working.
# This is required if you are going to add code after exiting the loop.
del pipeline 
del device            



