#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 发布 /turtle1/cmd_vel 话题，消息类型 geometry_msg：：Twist
import select
import sys
import termios, tty

import rospy
from geometry_msgs.msg import Twist
# from后边是自己的包.msg，也就是自己包的msg文件夹下，MyTwist是我的msg文件名MyTwist.msg
from vcu_pkg.msg import MyTwist

def vuc_publisher():
    # ROS node init
    rospy.init_node('vuc_publisher', anonymous=True)

    # 创建一个 publisher，发布名为 /turtle1/cmd_vel 的 topic，消息类型为 geometry_msgs::Twist，队列长度为 10
    turtle_vel_pub = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=1)

    # 设置循环频率
    rate = rospy.Rate(30)

    twist = Twist()  # 初始化 geometry_msgs::Twist 类型的消息

    rospy.loginfo('键盘输入 wsad 来控制运动方向： ')
    rospy.loginfo('按下 q 键盘退出')
    while not rospy.is_shutdown():
        # try:
        #     tty.setraw(fd)
        #     ch = sys.stdin.read(1)
        # finally:
        #     # 将终端还原为标准模式
        #     termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        try:
            if select.select([sys.stdin], [], [], 0)[0] == [sys.stdin]:
                ch = sys.stdin.read(1)
                rospy.loginfo('键盘输入： ' + ch)
                if ch == 'w':
                    # 前进方向速度 +1, speed_data范围 ：速度 -50 ～ 50 实际是 0～5m/s
                    twist.linear.x = min(twist.linear.x + 1, 50)
                elif ch == 's':
                    # 方向速度 -1, 范围 ：速度 -5.0 ～ 5.0
                    twist.linear.x = max(twist.linear.x - 1, -50)
                elif ch == 'a':
                    # 左拐 steer_data: 转向角 -24 ～ 24.0 度
                    twist.angular.z = min(twist.angular.z + 1, 24)
                elif ch == 'd':
                    twist.angular.z = max(twist.angular.z - 1, -24)
                elif ch == 'q':
                    exit()
        except Exception as e:
            rospy.logerr(e)
        # 发布消息
        turtle_vel_pub.publish(twist)
        rospy.loginfo('publish %0.2f m/s, %0.2f rad/s', twist.linear.x, twist.angular.z)

        rate.sleep()  # 按照上面设置的循环频率延时


if __name__ == '__main__':
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)  # 备份终端属性
    tty.setcbreak(sys.stdin.fileno())  # 设置属性
    try:
        vuc_publisher()
    except rospy.ROSInterruptException:
        pass
    finally:
        # 将终端还原为标准模式
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
