"""apple.py

Detect bottles

Packages needed for this script:

    - depthai

So we do not need any numpy/open-cv or anything.
"""

from pathlib import Path
import numpy as np
import cv2
import logging
import argparse

import depthai

CONFIG = {
    "streams": ["previewout", "metaout", "depth"],
    "ai": {
        "blob_file": str(
            Path("models/mobilenet-ssd/mobilenet-ssd.blob").resolve().absolute()
        ),
        "blob_file_config": str(
            Path("models/mobilenet-ssd/mobilenet-ssd.json").resolve().absolute()
        ),
        "calc_dist_to_bb": True,
        "camera_input": "right",
    },
}


def screen_position(detection, meta):
    """
    Get the x coordinate of the bounding box, calculate the center of the
    bounding box as a fraction of the screen width and convert this to: "left",
    "center" or "right".
    """
    loc = detection.x_max - detection.x_min / meta.getFrameWidth()
    if loc < 0.33:
        return "right"
    elif 0.33 < loc < 0.66:
        return "center"
    else:
        return "left"


def run(args):

    device = depthai.Device("", False)
    # Create the pipeline using the 'previewout, metaout & depth' stream,
    # establishing the first connection to the device.
    pipeline = device.create_pipeline(config=CONFIG)

    # pipeline has not been created succesfully, raise error.
    if pipeline is None:
        raise RuntimeError("Pipeline creation failed!")

    # We need an empty list
    detections = []
    cont = True
    out = None

    while cont:
        nnet_packets, data_packets = pipeline.get_available_nnet_and_data_packets()

        # Do detections
        for nnet_packet in nnet_packets:
            detections = list(nnet_packet.getDetectedObjects())

        for packet in data_packets:

            if packet.stream_name == "previewout":
                meta = packet.getMetadata()

                for detection in detections:
                    # bottle has label 5
                    if int(detection.label) == 5:
                        timestamp = meta.getTimestamp()
                        screen_pos = screen_position(detection, meta)
                        depth = detection.depth_z
                        logging.debug(f"{timestamp} : bottle : {screen_pos} : {depth}")

            if packet.stream_name == 'depth' and args.record:
                # get the depth frame
                window_name = packet.stream_name
                frame = packet.getData()
                frame = (65535 // frame).astype(np.uint8)
                frame = cv2.applyColorMap(frame, cv2.COLORMAP_HOT)

                # instantiate an output writer
                if not out:
                    height, width, channels = frame.shape
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter('output.mp4', fourcc, 20, (width, height))

                # Add frame to output video
                out.write(frame)

        if cv2.waitKey(1) == ord('q'):
            break

    # The pipeline object should be deleted after exiting the loop. Otherwise 
    # device will continue working. This is required if you are going to add 
    # code after exiting the loop.
    del pipeline
    del device

    # clean opencv nicely
    out.release()
    cv2.destroyAllWindows() 


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", default=False)
    args = parser.parse_args()

    logging.basicConfig(filename="joep.log", level=logging.DEBUG)
    run(args)
