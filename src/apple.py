"""apple.py

Detect bottles

Packages needed for this script:

    - depthai

So we do not need any numpy/open-cv or anything.
"""

from pathlib import Path
import logging

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


def screen_position(detection, meta) -> str:
    """
    :param depthai.Detection detection
    :param depthai.FrameMetadata meta
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


def run() -> None:

    device = depthai.Device("", False)
    # Create the pipeline using the 'previewout, metaout & depth' stream,
    # establishing the first connection to the device.
    pipeline = device.create_pipeline(config=CONFIG)

    # pipeline has not been created succesfully, raise error.
    if pipeline is None:
        raise RuntimeError("Pipeline creation failed!")

    # We need an empty list
    detections: list[depthai.Detection] = []
    cont = True

    while cont:
        nnet_packets: list[depthai.NNetPacket]
        data_packets: list[depthai.DataPacket]
        nnet_packets, data_packets = pipeline.get_available_nnet_and_data_packets()

        # Do detections
        for nnet_packet in nnet_packets:
            detections: list[depthai.Detection] = list(nnet_packet.getDetectedObjects())

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

    # The pipeline object should be deleted after exiting the loop. Otherwise 
    # device will continue working. This is required if you are going to add 
    # code after exiting the loop.
    del pipeline
    del device


if __name__ == "__main__":
    logging.basicConfig(filename="joep.log", level=logging.DEBUG)
    run()
