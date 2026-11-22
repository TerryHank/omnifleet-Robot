"""Jetson's installed nvjpegenc, with native OpenCV color conversion."""
import cv2
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst


class NvJpegEncoder:
    def __init__(self, width, height, quality):
        Gst.init(None)
        self.pipeline = Gst.parse_launch(
            f'appsrc name=source is-live=false format=time '
            f'caps=video/x-raw,format=I420,width={width},height={height},framerate=30/1 '
            f'! nvjpegenc quality={quality} ! appsink name=sink sync=false max-buffers=1 drop=true')
        self.source, self.sink = self.pipeline.get_by_name('source'), self.pipeline.get_by_name('sink')
        self.sequence = 0
        self.pipeline.set_state(Gst.State.PLAYING)

    def encode(self, image):
        yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV_I420)
        buffer = Gst.Buffer.new_wrapped(yuv.tobytes())
        buffer.pts = self.sequence * Gst.SECOND // 30
        self.sequence += 1
        if self.source.emit('push-buffer', buffer) != Gst.FlowReturn.OK:
            raise RuntimeError('nvjpegenc rejected image buffer')
        sample = self.sink.emit('try-pull-sample', Gst.SECOND)
        if sample is None:
            raise RuntimeError('nvjpegenc did not return a JPEG frame')
        result = sample.get_buffer()
        return result.extract_dup(0, result.get_size())

    def close(self):
        self.pipeline.set_state(Gst.State.NULL)
