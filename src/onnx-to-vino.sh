# goal: get pytorch models to run on our camera, which requires vino format.
# while now we run a mobilenet-ssd.blob (model format unknown) on our camera,
# we would like to explore the ability to run custom models, i.e. ONNX, converted from e.g. Torch.

# i followed the following guide to try and reach that goal.
# https://docs.openvinotoolkit.org/latest/openvino_docs_MO_DG_prepare_model_convert_model_Convert_Model_From_PyTorch.html

# get an ONNX model
python3 ./torch-to-onnx.py

# once we have an ONNX model:
# requires installing nix: https://nixos.org/download.html#nix-quick-install
nix-env -iA nixpkgs.openvino
pip install test-generator==0.1.1
# while one can try openvino off pip/github, i had trouble with this due to version mismatches.
bashs /nix/store/*-openvino-2021.2/deployment_tools/model_optimizer/install_prerequisites/install_prerequisites_onnx.sh

# still stuck, conversion to vino format still fails for unsupported model architectures.
# i've tried this on onnx files found online for models like mobilenet-ssd/yolov3/yolov4,
# but i haven't managed to run it on either so far.
# supported architectures:
# https://docs.openvinotoolkit.org/2021.4/openvino_docs_MO_DG_prepare_model_convert_model_Convert_Model_From_ONNX.html#supported_public_onnx_topologies
python3 /nix/store/*-openvino-2021.2/deployment_tools/model_optimizer/mo.py --input_model ./super_resolution-13.onnx --output_dir ./super_resolution/
