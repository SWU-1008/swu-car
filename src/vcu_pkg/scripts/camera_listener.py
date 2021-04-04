#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 发布 /image_view/image_raw 话题，消息类型
import rospy
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge


def callback(imgmsg):
    bridge = CvBridge()
    rospy.loginfo(
        'header' + str(imgmsg.header) + 'height' + str(imgmsg.height) + 'width' + str(imgmsg.width) + 'encoding' + str(
            imgmsg.encoding) + 'is_bigendian' + str(imgmsg.is_bigendian) + 'step' + str(imgmsg.step))
    img = bridge.imgmsg_to_cv2(imgmsg, "bgr8")
    cv2.imshow("listener", img)
    cv2.waitKey(3)


def listener():
    # In ROS, nodes are uniquely named. If two nodes with the same
    # node are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('camera_listener', anonymous=True)
    rospy.Subscriber("/image_view/image_raw", Image, callback)
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


if __name__ == '__main__':
    try:
        listener()
    except rospy.ROSInterruptException:
        pass
