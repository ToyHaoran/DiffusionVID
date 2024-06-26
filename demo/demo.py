import glob
import os
import argparse

# 参数
# configs/vid_R101.yaml
# models/mymodel_R101.pth
# --suffix
# ".JPEG"
# --visualize-path
# datasets/ILSVRC2015/Data/VID/val/ILSVRC2015_val_00022000
# --output-folder
# visualization

from mega_core.config import cfg
from predictor import VIDDemo

parser = argparse.ArgumentParser(description="PyTorch Object Detection Visualization")
parser.add_argument(
    "config",
    default="configs/vid_R_101_C4_1x.yaml",
    metavar="FILE",
    help="path to config file",
)
parser.add_argument(
    "checkpoint",
    default="R_101.pth",
    help="The path to the checkpoint for test.",
)
parser.add_argument(
    "--visualize-path",
    default="datasets/ILSVRC2015/Data/VID/val/ILSVRC2015_val_00003001",
    # default="datasets/ILSVRC2015/Data/VID/snippets/val/ILSVRC2015_val_00003001.mp4",
    help="the folder or a video to visualize.",
)
parser.add_argument(
    "--suffix",
    default=".JPEG",
    help="the suffix of the images in the image folder.",
)
parser.add_argument(
    "--output-folder",
    default="demo/visualization/",
    help="where to store the visulization result.",
)
parser.add_argument(
    "--video",
    action="store_true",
    help="if True, input a video for visualization.",
)
parser.add_argument(
    "--output-video",
    action="store_true",
    help="if True, output a video.",
)
parser.add_argument(
    "--track-refs",
    action="store_true",
    help="if True, output ref boxes for each current boxes.",
)
parser.add_argument(
    "--start-frame",
    type=int,
    default=0,
    help="demo inference starts from this frame_id",
)

args = parser.parse_args()
cfg.merge_from_file("configs/BASE_RCNN_1gpu.yaml")
# if 'Diffusion' in args.config:
from mega_core.modeling.detector.diffusion_det import add_diffusiondet_config
add_diffusiondet_config(cfg)
cfg.merge_from_file(args.config)
cfg.MODEL.VID.MEGA.MIN_OFFSET = -0
cfg.MODEL.VID.MEGA.MAX_OFFSET = 0  # 原0
cfg.MODEL.VID.MEGA.ALL_FRAME_INTERVAL = 1  # 原1
cfg.MODEL.VID.MEGA.KEY_FRAME_LOCATION = 0
cfg.INPUT.INFER_BATCH = 1  # 原1
# else:
#     cfg.merge_from_file(args.config)
cfg.merge_from_list(["MODEL.WEIGHT", args.checkpoint])  # load checkpoint path

name = os.path.split(args.config)[-1].split('.')[0]

model_name = os.path.join(cfg.MODEL.WEIGHT.split('/')[-2] + '_' +  cfg.MODEL.WEIGHT.split('/')[-1][:-4])
args.output_folder = args.output_folder + '/' + cfg.MODEL.VID.METHOD + '/' + model_name + '_' + args.visualize_path[-12:]

vid_demo = VIDDemo(
    cfg,
    video=args.video,
    method=cfg.MODEL.VID.METHOD,
    confidence_threshold=0.3,
    output_folder=args.output_folder
)

if not args.video:
    visualization_results = vid_demo.run_on_image_folder(
        args.visualize_path, suffix=args.suffix, track_refs=args.track_refs, start_frame=args.start_frame)
else:
    visualization_results = vid_demo.run_on_video(args.visualize_path, start_frame=args.start_frame)

if not args.output_video:
    vid_demo.generate_images(visualization_results)
else:
    vid_demo.generate_video(visualization_results)