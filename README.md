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
