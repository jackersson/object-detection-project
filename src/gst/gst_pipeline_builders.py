import os

from .utils import get_media_source_type, MediaSourceType


def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def bool_to_string(flag):
    """
        Converts bool to string

        Args:
            flag: bool

        Returns:
            result: str ("true"/"false")
    """
    return "true" if flag else "false"


def to_gst_pipeline(source, modules=[], index=0, show_window=False, show_fps=False, sync=False,
                    video_record_location=None, video_record_duration=60):
    source_type = get_media_source_type(source)

    if source_type == MediaSourceType.FILE:
        return gst_pipeline_from_file(source, modules, index=index, show_window=show_window, show_fps=show_fps,
                                      video_record_location=video_record_location,
                                      video_record_duration=video_record_duration, sync=sync)

    raise NotImplementedError("Gst Pipeline Not Implemented")


def gst_pipeline_from_file(filename, modules=[], index=0, show_window=False, show_fps=False, sync=False,
                           video_record_location=None, video_record_duration=60):

    assert os.path.isfile(filename)

    plugins = "filesrc location={} ! ".format(filename)
    plugins += "decodebin ! "
    plugins += "videoconvert ! "
    plugins += "video/x-raw,format=RGB ! "
    plugins += "videoconvert ! "

    for module in modules:
        plugins += "gstplugin_py name={} ! ".format(module)

    plugins += "videoconvert ! "

    plugins += gst_sink(index, show_window=show_window,
                        show_fps=show_fps, sync=sync, video_record_location=video_record_location,
                        video_record_duration=video_record_duration)

    '''
    is_sync = "sync=True" if sync else "sync=False"
    sink = "gtksink" if show_window else "fakesink"

    if show_fps:
        fps_plugin_name = "fps_{}".format(index)
        plugins += "fpsdisplaysink video-sink=={} sync={} name={} ".format(
            sink, bool_to_string(sync), fps_plugin_name)
    else:
        plugins += "{} sync={} ".format(sink, bool_to_string(sync))
    '''
    return plugins


def gst_sink(index, show_window=False, show_fps=False, sync=False,
             video_record_location=None, video_record_duration=60):

    plugins = ""

    # is_sync = "sync=True" if sync else "sync=False"
    sink = "gtksink" if show_window else "fakesink"

    if video_record_location:
        create_dir(os.path.dirname(video_record_location))

    tee_name = "t0_{}".format(index)
    _video_record_duration = video_record_duration * 10**9
    if show_fps:
        if video_record_location:
            plugins += "tee name={} ! queue leaky=1 ! videoconvert ! ".format(
                tee_name)

        fps_plugin_name = "fps_{}".format(index)
        plugins += "fpsdisplaysink video-sink={} sync={} name={} ".format(
            sink, bool_to_string(sync), fps_plugin_name)

        if video_record_location:
            plugins += "{}. ! queue ! x264enc tune=zerolatency ! ".format(
                tee_name)
            plugins += "splitmuxsink location={} max-size-time={} sync={} ".format(video_record_location,
                                                                                   _video_record_duration,
                                                                                   bool_to_string(sync))
    elif show_window:
        if video_record_location:
            plugins += "tee name={} ! queue leaky=1 ! videoconvert ! ".format(
                tee_name)

        plugins += "gtksink sync={} ".format(bool_to_string(sync))

        if video_record_location:
            plugins += "{}. ! queue ! x264enc tune=zerolatency ! ".format(
                tee_name)
            plugins += "splitmuxsink location={} max-size-time={} sync={} ".format(video_record_location,
                                                                                   _video_record_duration,
                                                                                   bool_to_string(sync))
    else:
        if video_record_location:
            plugins += "x264enc tune=zerolatency ! "
            plugins += "splitmuxsink location={} max-size-time={} sync={} ".format(video_record_location,
                                                                                   _video_record_duration,
                                                                                   bool_to_string(sync))
        else:
            plugins += "fakesink sync={} ".format(sink, bool_to_string(sync))

    return plugins
