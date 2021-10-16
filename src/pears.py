import argparse
from pathlib import Path

import depthai as dai
import cv2.cv2 as cv2

SHOW_OUTPUT = False
LOG_FNAME = "joep.log"


def draw_frame(imgFrame, pos):
    frame = imgFrame.getCvFrame()
    return cv2.putText(
        frame,
        f"pos: {pos}",
        (10, 30),
        cv2.FONT_HERSHEY_TRIPLEX,
        0.6,
        (255, 255, 255),
    )


def map_pos(det):
    xmean = (det.xmax + det.xmin) / 2
    if xmean < 0.33:
        return "1"
    elif 0.33 < xmean < 0.66:
        return "2"
    else:
        return "3"


def run() -> None:
    nnPath = str(Path("models/mobilenet-ssd/mobilenet-ssd.blob").resolve().absolute())

    # =================================================================================
    # SETUP
    # =================================================================================

    print("[INFO] Setting up camera connection and building data pipelines on camera.")
    # We need a pipeline. The pipeline runs on the device and we can ".get()" the output
    # of the different streams/components.

    # TODO: since we do not use the camRgb, try to remove it for some performance
    #   improvements.
    pipeline = dai.Pipeline()

    camRgb = pipeline.createColorCamera()
    nn = pipeline.createMobileNetDetectionNetwork()
    xoutRgb = pipeline.createXLinkOut()
    nnOut = pipeline.createXLinkOut()

    xoutRgb.setStreamName("rgb")
    nnOut.setStreamName("nn")

    camRgb.setPreviewSize(300, 300)
    camRgb.setInterleaved(False)
    camRgb.setFps(40)

    nn.setConfidenceThreshold(0.5)
    nn.setBlobPath(nnPath)
    nn.setNumInferenceThreads(2)
    nn.input.setBlocking(False)

    nn.passthrough.link(xoutRgb.input)

    camRgb.preview.link(nn.input)
    nn.out.link(nnOut.input)

    f = open(LOG_FNAME, "w")

    # =================================================================================
    # RUN
    # =================================================================================

    try:
        print("[INFO] starting bottle detection")
        # Connect to device and start pipeline
        with dai.Device(pipeline) as device:

            # Output queues will be used to get the rgb frames and nn data from the
            # outputs defined above
            qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            qDet = device.getOutputQueue(name="nn", maxSize=4, blocking=False)

            while True:

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
                output_string = f"{pos}1"
                f.write(output_string)

                if SHOW_OUTPUT:
                    imgFrame = qRgb.get()
                    # Write the position on the frame
                    cv2.imshow("PEAR", draw_frame(imgFrame, pos))

                if cv2.waitKey(1) == ord("q"):
                    break

    finally:
        print("[WARNING] closing file")
        f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--show", dest="SHOW_OUTPUT", action="store_true")
    parser.parse_args()
    run()
