#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 发布 /turtle1/cmd_vel 话题，消息类型 geometry_msg：：Twist

import rospy
from geometry_msgs.msg import Twist
from Can_Utils import CanUtil
# from后边是自己的包.msg，也就是自己包的msg文件夹下，MyTwist是我的msg文件名MyTwist.msg
from vcu_pkg.msg import MyTwist

can_util = CanUtil()


def callback(twist):
    can_util.drive(twist)
    rospy.loginfo(twist)


def vuc_controller():
    # ROS node init
    rospy.init_node('vuc_control_node', anonymous=True)

    # 创建一个 Subscriber，订阅名为 /turtle1/cmd_vel 的 topic，消息类型为 geometry_msgs::Twist，队列长度为 1
    rospy.Subscriber('/cmd_vel', MyTwist, callback, queue_size=1)

    rospy.spin()


if __name__ == '__main__':
    try:
        vuc_controller()
    except rospy.ROSInterruptException:
        pass
