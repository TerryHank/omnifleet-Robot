#!/usr/bin/env python3
"""红、黄、绿、蓝 HSV 颜色识别节点。"""

import rclpy
import cv2
import json
from std_msgs.msg import String
from color_picker import ColorPicker, recognize_picked

try:
    from .algorithms import recognize_colors
    from .ros_support import ClassicalVisionNode
except ImportError:
    from algorithms import recognize_colors
    from ros_support import ClassicalVisionNode


class ColorRecognitionNode(ClassicalVisionNode):
    """识别画面中的主要颜色区域。"""

    def __init__(self) -> None:
        super().__init__("color_recognition", "/camera/color/image_raw")
        self.declare_parameter("minimum_area", 200.0)
        self.declare_parameter("selected_color", "")
        self.color_picker = ColorPicker(self)
        self.selected_output = self.create_publisher(String,'/vision/color/selected',1) if self.color_picker.enabled else None
        self.color_callback = self.add_on_set_parameters_callback(self.on_color_parameters)

    def on_color_parameters(self, parameters):
        from rcl_interfaces.msg import SetParametersResult
        for parameter in parameters:
            picked = self.color_picker.selection
            if parameter.name=='selected_color' and self.get_parameter('selected_color').value and parameter.value not in ('',self.get_parameter('selected_color').value):
                return SetParametersResult(successful=False,reason='请先清除跟踪，再选择其他颜色')
            if parameter.name == "selected_color" and parameter.value not in ("", "red", "yellow", "green", "blue") and not (picked and parameter.value == picked['name']):
                return SetParametersResult(successful=False, reason="selected_color must be red/yellow/green/blue or empty")
        return SetParametersResult(successful=True)

    def image_callback(self, message) -> None:
        """识别颜色区域并发布边界框和面积。"""
        try:
            image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
            selected = str(self.get_parameter("selected_color").value)
            minimum_area = float(self.get_parameter("minimum_area").value)
            if self.color_picker.selection is not None and selected == self.color_picker.selection['name']:
                debug,result = recognize_picked(image,self.color_picker.selection,minimum_area)
            else:
                debug,result = recognize_colors(image,minimum_area,selected)
            self.color_picker.remember(message,image,result['detections'])
            if self.selected_output is not None:
                followed=result['detections'] if selected else []
                payload=dict(result,detections=followed,stamp=dict(sec=message.header.stamp.sec,nanosec=message.header.stamp.nanosec),
                             frame_id=message.header.frame_id,image_width=message.width,image_height=message.height)
                payload.update(count=len(payload['detections']),detected=bool(payload['detections']))
                self.selected_output.publish(String(data=json.dumps(payload,separators=(',',':'))))
                for item in followed:
                    x,y,w,h=map(int,item['bbox']);cv2.rectangle(debug,(x,y),(x+w,y+h),(255,255,255),3)
                result=dict(result,selected_detections=followed)
            result['detection_mode']='selected_only' if selected else 'all_colors'
            result['selection_locked']=bool(selected)
            result["selected_color"] = selected
            result["pick_result"] = self.color_picker.result
            result["picked_color"] = self.color_picker.selection
            self.publish_result(message, debug, result)
        except Exception as error:
            self.get_logger().error(f"颜色识别失败：{error}")


def main(args=None) -> None:
    """启动颜色识别节点。"""
    rclpy.init(args=args)
    node = ColorRecognitionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
