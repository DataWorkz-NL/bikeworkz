#!/usr/bin/env python3

# python core modules
import sys
import logging
import argparse

# 3rd party modules
import cv2
import numpy as np
import depthai as dai

def run(args):
	logging.info('initializing')

	# Closer-in minimum depth, disparity range is doubled (from 95 to 190):
	extended_disparity = False
	# Better accuracy for longer distance, fractional disparity 32-levels:
	subpixel = False
	# Better handling for occlusions:
	lr_check = False

	recorder = None

	# Create pipeline
	pipeline = dai.Pipeline()

	# Define sources and outputs
	monoLeft = pipeline.createMonoCamera()
	monoRight = pipeline.createMonoCamera()
	depth = pipeline.createStereoDepth()
	xout = pipeline.createXLinkOut()

	xout.setStreamName("disparity")

	# Properties
	monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
	monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
	monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
	monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

	# Create a node that will produce the depth map (using disparity output as it's easier to visualize depth this way)
	depth.initialConfig.setConfidenceThreshold(200)
	# Options: MEDIAN_OFF, KERNEL_3x3, KERNEL_5x5, KERNEL_7x7 (default)
	depth.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
	depth.setLeftRightCheck(lr_check)
	depth.setExtendedDisparity(extended_disparity)
	depth.setSubpixel(subpixel)

	# Linking
	monoLeft.out.link(depth.left)
	monoRight.out.link(depth.right)
	depth.disparity.link(xout.input)

	# Connect to device and start pipeline
	with dai.Device(pipeline) as device:
		logging.info('Start process')

		# Output queue will be used to get the disparity frames from the outputs defined above
		q = device.getOutputQueue(name="disparity", maxSize=4, blocking=False)

		# initialize the frames
		previous_frame = None

		# loop it
		while True:
			inDepth = q.get()  # blocking call, will wait until a new data has arrived
			frame = inDepth.getFrame()

			# Normalization for better visualization
			frame = (frame * (255 / depth.initialConfig.getMaxDisparity())).astype(np.uint8)

			# get the frame dimensions
			width, height = frame.shape
			x = int(width / 4)
			y = int(height / 4)
			w = int(width / 2)
			h = int(height / 2)

			# initialize the frames
			acceleration_frame = frame
			ROI = frame[x:x+w, y:y+h]

			if previous_frame is not None:

				# get the acceleration per pixel
				acceleration_frame = previous_frame - frame

				# crop to region of interest
				ROI = acceleration_frame[x:x+w, y:y+h]

				# remove the noise from the mask
				kernel = np.ones((5,5), np.uint8)
				ROI = cv2.erode(ROI, kernel, iterations=2)

				if np.sum(ROI) > args.alert_threshold:
					logging.warning('COLLISION ALLERT')

			# update the previous frame
			previous_frame = frame

			# show the output
			if args.show:

				# convert mask to BGR format
				frame_bgr = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

				# Available color maps: https://docs.opencv.org/3.4/d3/d50/group__imgproc__colormap.html
				frame_coloured = cv2.applyColorMap(frame, cv2.COLORMAP_JET)

				# overlay ROI to frame
				frame_coloured_roi = frame.copy()
				frame_coloured_roi[x:x+w, y:y+h] = ROI
				frame_coloured_roi = cv2.applyColorMap(frame_coloured_roi, cv2.COLORMAP_JET)

				# show it
				combined = cv2.hconcat([frame_bgr, frame_coloured_roi])

				# record the files
				if args.record:
					if not recorder:
						height, width, channels = combined.shape
						fourcc = cv2.VideoWriter_fourcc(*'mp4v')
						recorder = cv2.VideoWriter('output.mp4', fourcc, 20, (width, height))

					# Add frame to output video
					recorder.write(combined)

				cv2.imshow("combined", combined)

			if cv2.waitKey(1) == ord('q'):
				break


if __name__ == "__main__":
	logging.basicConfig(
		format='[%(asctime)s] %(levelname)s - %(message)s',
		stream=sys.stdout, 
		level=logging.DEBUG
	)

	parser = argparse.ArgumentParser()
	parser.add_argument("-s", "--show", action='store_true')
	parser.add_argument("-r", "--record", action='store_true')
	parser.add_argument("-t", "--alert_threshold", default=1000000)
	args = parser.parse_args()

	run(args)