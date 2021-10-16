# TODO:
#   - [ ] Test current script
#   - [ ] Add stream with detph per pixel
#   - [ ] Combine depth with roi of tracked objects
#   - [ ] Plot 3D trajectory of tracked objects

from pathlib import Path
import cv2.cv2 as cv2
import depthai as dai
import numpy as np
import time
import argparse

nnPath = Path("models/mobilenet-ssd/mobilenet-ssd.blob")
parser = argparse.ArgumentParser()
parser.add_argument(
    "-ff",
    "--full_frame",
    action="store_true",
    help="Perform tracking on full RGB frame",
    default=False,
)

args = parser.parse_args()

fullFrameTracking = args.full_frame

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
camRgb = pipeline.createColorCamera()
detectionNetwork = pipeline.createMobileNetDetectionNetwork()
objectTracker = pipeline.createObjectTracker()

xlinkOut = pipeline.createXLinkOut()
trackerOut = pipeline.createXLinkOut()

xlinkOut.setStreamName("preview")
trackerOut.setStreamName("tracklets")

# Properties
camRgb.setPreviewSize(300, 300)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
camRgb.setInterleaved(False)
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
camRgb.setFps(40)

# testing MobileNet DetectionNetwork
detectionNetwork.setBlobPath(str(nnPath))
detectionNetwork.setConfidenceThreshold(0.5)
detectionNetwork.input.setBlocking(False)

# objectTracker.setDetectionLabelsToTrack([15])  # track only person
objectTracker.setDetectionLabelsToTrack([5])
# possible tracking types: ZERO_TERM_COLOR_HISTOGRAM, ZERO_TERM_IMAGELESS
objectTracker.setTrackerType(dai.TrackerType.ZERO_TERM_COLOR_HISTOGRAM)
# take the smallest ID when new object is tracked, possible options: SMALLEST_ID, UNIQUE_ID
objectTracker.setTrackerIdAssigmentPolicy(dai.TrackerIdAssigmentPolicy.SMALLEST_ID)

# Linking
camRgb.preview.link(detectionNetwork.input)
objectTracker.passthroughTrackerFrame.link(xlinkOut.input)

if fullFrameTracking:
    camRgb.video.link(objectTracker.inputTrackerFrame)
else:
    detectionNetwork.passthrough.link(objectTracker.inputTrackerFrame)

detectionNetwork.passthrough.link(objectTracker.inputDetectionFrame)
detectionNetwork.out.link(objectTracker.inputDetections)
objectTracker.out.link(trackerOut.input)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:

    preview = device.getOutputQueue("preview", 4, False)
    tracklets = device.getOutputQueue("tracklets", 4, False)

    startTime = time.monotonic()
    counter = 0
    fps = 0
    frame = None

    while True:
        # TODO: Is it possible to also get a stream with depth information?
        imgFrame = preview.get()
        track = tracklets.get()

        counter += 1
        current_time = time.monotonic()
        if (current_time - startTime) > 1:
            fps = counter / (current_time - startTime)
            counter = 0
            startTime = current_time

        color = (255, 255, 0)
        frame = imgFrame.getCvFrame()

        trackletsData = track.tracklets

        for t in trackletsData:
            roi = t.roi.denormalize(frame.shape[1], frame.shape[0])
            x1 = int(roi.topLeft().x)
            y1 = int(roi.topLeft().y)
            x2 = int(roi.bottomRight().x)
            y2 = int(roi.bottomRight().y)

            label = "bottle"

            cv2.putText(
                frame,
                str(label),
                (x1 + 10, y1 + 20),
                cv2.FONT_HERSHEY_TRIPLEX,
                0.5,
                255,
            )
            cv2.putText(
                frame,
                f"ID: {[t.id]}",
                (x1 + 10, y1 + 35),
                cv2.FONT_HERSHEY_TRIPLEX,
                0.5,
                255,
            )
            cv2.putText(
                frame,
                t.status.name,
                (x1 + 10, y1 + 50),
                cv2.FONT_HERSHEY_TRIPLEX,
                0.5,
                255,
            )
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, cv2.FONT_HERSHEY_SIMPLEX)

        cv2.putText(
            frame,
            "NN fps: {:.2f}".format(fps),
            (2, frame.shape[0] - 4),
            cv2.FONT_HERSHEY_TRIPLEX,
            0.4,
            color,
        )

        cv2.imshow("tracker", frame)

        if cv2.waitKey(1) == ord("q"):
            break
