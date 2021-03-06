import os
import logging
import tensorflow as tf

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

GObject.threads_init()
Gst.init(None)

from src.gst import GstPipeline as Pipeline
from src.gst import GstPipelinesController as PipelinesController
from src.gst import GstBufferToFrameDataAdapter
from src.object_detection import TfObjectDetectionModel

from src.base import ModuleInfo
from src.modules import *

from view import ColorPicker, OverlayOpenCV

from utils import load_labels_pbtxt

tf.logging.set_verbosity(tf.logging.ERROR)
logging.basicConfig(level=0)

# Create object that launches Gstreamer Pipelines
pipelines_controller = PipelinesController()

# VIDEO FILENAME
# /home/taras/coder/projects/object-detection-project/data/videos/MOT17-09.mp4"  # "video.mp4"
# VIDEO_FILENAME = "/home/taras/coder/projects/object-detection-project/data/videos/video000.mp4"
# VIDEO_FILENAME = "/home/taras/Documents/marichka.mp4"
#

# Several FILENAMES
VIDEO_FILENAMES = [
    "/home/taras/coder/projects/object-detection-project/data/videos/video000.mp4",
    "/home/taras/coder/projects/object-detection-project/data/videos/video000.mp4"
]

LABELS_FILE = os.path.join("data/mscoco_label_map.pbtxt")
WEIGHTS = "data/models/ssdlite_mobilenet_v2_coco_2018_05_09/frozen_inference_graph.pb"

# Load labels
labels = load_labels_pbtxt(LABELS_FILE)

# Create Object Detector
object_detector = TfObjectDetectionModel(
    WEIGHTS, device='/device:GPU:0', threshold=0.1, labels=labels)

# FIRST PIPELINE
# Simple bin of elements
module_bin_1 = Bin([
    FrameDataSource(),  # Create Frame Data
    # Convert Gst.Buffer to image and update FrameData.color
    GstBufferToFrameDataAdapter(),
    # Run Object Detection on frame and fill FrameData.objects
    ObjectDetectorAdapter(object_detector),
    OverlayOpenCV(ColorPicker(n_colors=len(labels)))  # Draw objects on frame
])


# SECOND PIPELINE
# Simple bin of elements
module_bin_2 = Bin([
    FrameDataSource(),  # Create Frame Data
    # Convert Gst.Buffer to image and update FrameData.color
    GstBufferToFrameDataAdapter(),
    # Run Object Detection on frame and fill FrameData.objects
    ObjectDetectorAdapter(object_detector),
    OverlayOpenCV(ColorPicker(n_colors=len(labels)))  # Draw objects on frame
])

bins = [module_bin_1, module_bin_2]

index = 0
for filename, bn in zip(VIDEO_FILENAMES, bins):

    pipeline = Pipeline(source=VIDEO_FILENAME,
                        modules=[ModuleInfo(module=bn)],
                        show_window=True,
                        show_fps=True,
                        video_record_location=os.path.join(
                            os.path.abspath("output/{}".format(index)), "video%03d.mp4"),
                        video_record_duration=60,  # sec
                        index=index
                        )

    # Add pipeline to PipelinesController
    pipelines_controller.append(pipeline)

    index += 1

pipelines_controller.run()
