import argparse
import logging
from pathlib import Path
import time

import numpy as np
import depthai as dai
import cv2.cv2 as cv2

SHOW_OUTPUT = False
LOG_FNAME = "joep.log"


def draw_frame(imgFrame, pos, acceleration_int, fps):
    frame = imgFrame.getCvFrame()

    cv2.putText(
        frame,
        f"pos: {pos}",
        (10, 30),
        cv2.FONT_HERSHEY_TRIPLEX,
        0.6,
        (255, 255, 255),
    )

    cv2.putText(
        frame,
        f"acc: {acceleration_int}",
        (10, 50),
        cv2.FONT_HERSHEY_TRIPLEX,
        0.6,
        (255, 255, 255),
    )

    cv2.putText(
        frame,
        f"fps: {fps}",
        (10, 70),
        cv2.FONT_HERSHEY_TRIPLEX,
        0.6,
        (255, 255, 255),
    )

    return frame


def map_pos(det):
    xmean = (det.xmax + det.xmin) / 2
    if xmean < 0.33:
        return "3"
    elif 0.33 < xmean < 0.66:
        return "2"
    else:
        return "1"


def depth_to_frame(qDepth, depth):
    depth_frame = qDepth.get().getFrame()
    depth_frame = (depth_frame * (255 / depth.initialConfig.getMaxDisparity())).astype(
        np.uint8
    )
    return depth_frame


def map_acceleration_fraction(i):
    if i > 0.00105:
        return "0"
    elif 0.0008 < i < 0.00105:
        return "1"
    elif i < 0.0008:
        return "2"
    else:
        # something went wrong
        logging.warning(f"something weird happend during acceleration mapping, i: {i}")
        return "0"


def run() -> None:
    nnPath = str(Path("models/mobilenet-ssd/mobilenet-ssd.blob").resolve().absolute())

    # =================================================================================
    # SETUP
    # =================================================================================

    logging.info("Setting up camera connection and building data pipelines on camera.")
    # We need a pipeline. The pipeline runs on the device and we can ".get()" the output
    # of the different streams/components.

    pipeline = dai.Pipeline()

    camRgb = pipeline.createColorCamera()
    nn = pipeline.createMobileNetDetectionNetwork()
    xoutRgb = pipeline.createXLinkOut()
    nnOut = pipeline.createXLinkOut()

    monoLeft = pipeline.createMonoCamera()
    monoRight = pipeline.createMonoCamera()
    depth = pipeline.createStereoDepth()
    depth_out = pipeline.createXLinkOut()  # xout

    xoutRgb.setStreamName("rgb")
    nnOut.setStreamName("nn")
    depth_out.setStreamName("depth")

    camRgb.setPreviewSize(300, 300)
    camRgb.setInterleaved(False)
    camRgb.setFps(40)

    nn.setConfidenceThreshold(0.5)
    nn.setBlobPath(nnPath)
    nn.setNumInferenceThreads(2)
    nn.input.setBlocking(False)

    # Properties
    monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
    monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

    # Create a node that will produce the depth map (using disparity output as it's
    # easier to visualize depth this way)
    depth.initialConfig.setConfidenceThreshold(200)
    depth.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)

    nn.passthrough.link(xoutRgb.input)
    camRgb.preview.link(nn.input)

    monoLeft.out.link(depth.left)
    monoRight.out.link(depth.right)
    depth.disparity.link(depth_out.input)

    nn.out.link(nnOut.input)

    logging.info("sucessfully initialized camera and neural network")

    f = open(LOG_FNAME, "w")
    logging.info(f"writing processed detections to: {LOG_FNAME}")

    # =================================================================================
    # RUN
    # =================================================================================

    data = []
    try:
        logging.info("starting bottle detection")
        # Connect to device and start pipeline

        with dai.Device(pipeline) as device:

            # for fps
            startTime = time.monotonic()
            counter = 0
            acceleration_box = None

            # Output queues will be used to get the rgb frames and nn data from the
            # outputs defined above
            qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            qDet = device.getOutputQueue(name="nn", maxSize=4, blocking=False)
            qDepth = device.getOutputQueue(name="depth", maxSize=4, blocking=False)

            previous_frame = None
            fps = 0

            while True:

                counter += 1
                current_time = time.monotonic()
                if (current_time - startTime) > 1:
                    fps = counter / (current_time - startTime)
                    counter = 0
                    startTime = current_time

                # Use blocking get() call to catch frame and inference result synced
                inDet = qDet.get()
                # If there is no detection there is nothing to do (detections can be
                # empty though)
                if inDet is None:
                    continue

                # Check if we detect a bottle (label number 5).
                detected = False
                for detection in inDet.detections:
                    if int(detection.label) == 5:
                        detected = True
                        det = detection

                depth_frame = depth_to_frame(qDepth, depth)
                acceleration_int = "0"

                if detected and previous_frame is not None:

                    # We need the with and hight of the video depth frame because we
                    # need to calculate back the pixel coordinates.
                    (w, h) = depth_frame.shape
                    xmax, xmin = int(det.xmax * w), int(det.xmin * w)
                    ymax, ymin = int(det.ymax * h), int(det.ymin * h)

                    # Cut out the regions of interest (the bounding boxes in out current
                    # frame)
                    depth_box = depth_frame[ymin:ymax, xmin:xmax]
                    prev_box = previous_frame[ymin:ymax, xmin:xmax]

                    # Calculate (and scale) the speed in the bounding box. This is
                    # simply the difference between the depth in the previous frame and
                    # the current frame.
                    acceleration_box = (((prev_box - depth_box) + 255) / 2).astype(
                        np.uint8
                    )

                    pixel_acceleraction = np.mean(
                        acceleration_box
                        / (acceleration_box.shape[0] * acceleration_box.shape[1])
                    )

                    data.append(pixel_acceleraction)

                    # Number of pixels * max value per pixel
                    max_acceleration = (
                        acceleration_box.shape[0] * acceleration_box.shape[1] * 255
                    )

                    logging.info(
                        f"max: {max_acceleration}, "
                        f"sum: {np.sum(acceleration_box)} "
                        f"actual frac: {np.sum(acceleration_box)/max_acceleration}"
                        f"pixel: {pixel_acceleraction}"
                    )

                    # Map the acceleration fraction that we just calculated to some
                    # bins.
                    acceleration_int = map_acceleration_fraction(
                        np.sum(acceleration_box) / max_acceleration
                    )

                previous_frame = depth_frame

                # Determine the center position of the bounding box and convert this to
                # a "0", "1", "2", "3" depending on the location of the detected object
                # in the screen. The coordinates are between 0.0 and 1.0.
                if detected:
                    pos = map_pos(det)
                else:
                    # No detection
                    pos = "0"

                # Go the the beginning of the output file and write the output to the
                # first line.
                #
                # TODO: replace the "1" in the input string with some number that will
                #   report the depth of the detected object.
                f.seek(0)
                output_string = f"{pos}{acceleration_int}"
                f.write(output_string)

                if SHOW_OUTPUT:

                    # Normal footage, write files to this
                    img_frame = qRgb.get()
                    cv2.imshow(
                        "PEAR", draw_frame(img_frame, pos, acceleration_int, fps)
                    )

                    if acceleration_box is not None:
                        depth_frame[ymin:ymax, xmin:xmax] = acceleration_box

                    cv2.imshow("depth", depth_frame)

                if cv2.waitKey(1) == ord("q"):
                    break

    finally:
        logging.warning("closing file")

        print("mean", np.mean(np.array(data)))

        with open("acc.dat", "w") as f:
            for d in data:
                f.write(f"{d}\n")
        f.close()


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    logging.info(
        "detect bottles, their position (on screen) as well as depth of the object"
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()

    if args.show:
        SHOW_OUTPUT = True

    logging.info(f"commandline arguments parse, SHOW_OUTPUT: {SHOW_OUTPUT}")

    run()
