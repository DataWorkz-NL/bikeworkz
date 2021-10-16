# Bikeworkz

## Installation

``` bash
pip install -r requirements.txt
```

## Demo

``` bash
cd src
python demo/Streaming_4K_Camera.py
python demo/Object_Detection_RGB.py
python demo/Object_Detection_Left_Right.py
python demo/Monocular-Neural-Inference-fused-with-Stereo-Depth.py
```

## First attempt to run on raspberry pi: `apple.py`

A simple script that will recognise a bottle (the pretrained model does not recognise
apples it turns out). The output of this script is whether or not a bottle is on screen,
the location of the bottle (left, center and right) and the distance. These metrics
should be written to a file where another running process can pick up this output and
control the output pins of the Raspberry Pi that are connected to LED’s. The end product
should be a device that will light up when a bottle is in view. If it is in the middle
the signal will change/get more intense.

### How to install and use

On the Raspberry Pi, install a recent version of python (3.9 in our case). And use the
following to install the dependencies for `depthai`, the python package that controls
and reads from the camera:

``` bash
sudo curl -fL http://docs.luxonis.com/_static/install_dependencies.sh | bash
```

Once the dependencies are installed, run:

``` bash
pip install depthai
```

In a (virtual) python environment. If `depthai` is successfully installed the script to
start the camera and start detecting the bottles:

``` bash
python src/apple.py
```

This should start writing detections (of bottles) to a file.

### Notes

To run examples in [depthai-python](https://github.com/luxonis/depthai-python), first
run:

``` bash
git clone git@github.com:luxonis/depthai-python.git
cd depthai-python/examples
python install_requirements.txt
```

- Make sure Raspian OS is up to date (libc6)
- Python 3.9
- libc6: >= 2.30
- glibcxx_3.4.26

## 2021-10-16, 16:42 - Something is working

The script `src/pears.py` is now able to run on a Raspberry Pi. This means that we can
run object detection on the camera and periodically update a file that will either
contain a simple `0` or a `1`. The script `src/joep.py` will continually read the output
file from `src/pears.py` and based on the number turn on an orange or a red LED.

## Communication

Communication between camera (script) and arduino is done by writing to a file. This
file contains two digits, which will determine the combination of LED's turning on:

- Position 1:
  - 0: No object detected
  - 1: Object detected on the left
  - 2: Object detected in the center
  - 3: Object detected on the right
- Position 2:
  - 0: Moves away from me - warning - green/yellow
  - 1: Moves closer to me (slowly) - yellow/read
  - 2: Moves alarmingly fast closer to me - red/blinking
