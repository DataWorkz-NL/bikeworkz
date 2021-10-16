from pathlib import Path
import depthai as dai

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

    f = open("joep.log", "w")

    # =================================================================================
    # RUN
    # =================================================================================

    try:
        print("[INFO] starting bottle detection")
        # Connect to device and start pipeline
        with dai.Device(pipeline) as device:

            # Output queues will be used to get the rgb frames and nn data from the outputs
            # defined above
            qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            qDet = device.getOutputQueue(name="nn", maxSize=4, blocking=False)

            while True:
                # Use blocking get() call to catch frame and inference result synced
                inDet = qDet.get()

                if inDet is None:
                    continue

                detected = False
                for detection in inDet.detections:
                    if int(detection.label) == 5:
                        detected = True

                if detected:
                    output = "1"
                else:
                    output = "0"

                f.seek(0)
                f.write(output)
    finally:
        print("[WARNING] closing file")
        f.close()


if __name__ == "__main__":
    run()
