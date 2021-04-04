#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 发布 /image_view/image_raw 话题，消息类型

import sys
import rospy
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge
from std_msgs.msg import Header
import numpy as np


def camera_publisher():
    # ROS node init
    rospy.init_node('camera_publisher', anonymous=True)
    bridge = CvBridge()

    img_pub = rospy.Publisher('/image_view/image_raw', Image, queue_size=1)

    # 设置循环频率
    rate = rospy.Rate(30)

    camera_id = 0
    cap = cv2.VideoCapture(camera_id)

    # ros_frame = Image()
    # h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    # w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    # ros_frame.header.frame_id = "Camera"
    # ros_frame.height = h
    # ros_frame.width = w
    # ros_frame.encoding = "bgr8"

    rospy.loginfo('开启 {} 号摄像头，发布 主题 /image_view/image_raw'.format(camera_id))
    while not rospy.is_shutdown():
        ret, img = cap.read()
        if ret:
            # ros_frame.data = np.array(img).tostring()  # 图片格式转换
            # cv2_to_imgmsg 干了这么一长串事情
            ros_frame = bridge.cv2_to_imgmsg(img, "bgr8")
            ros_frame.header.stamp = rospy.Time.now()
            ros_frame.header.frame_id = "Camera_{}".format(camera_id)
            img_pub.publish(ros_frame)  # 发布消息

        else:
            rospy.loginfo('摄像头 {} 采集图像失败'.format(camera_id))
        rate.sleep()  # 按照上面设置的循环频率延时
    cap.release()


if __name__ == '__main__':
    try:
        camera_publisher()
    except rospy.ROSInterruptException:
        pass
