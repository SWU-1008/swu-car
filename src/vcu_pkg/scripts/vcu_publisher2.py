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
    turtle_vel_pub = rospy.Publisher('/cmd_vel', MyTwist, queue_size=1)

    # 设置循环频率
    rate = rospy.Rate(30)

    my_twist = MyTwist()  # 初始化 自定义的 geometry_msgs::Twist 类型的消息
    my_twist.cl = 0.0  # 初始判定为未越界
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
                    my_twist.twist.linear.x = min(my_twist.twist.linear.x + 1, 50)
                elif ch == 's':
                    # 方向速度 -1, 范围 ：速度 -5.0 ～ 5.0
                    my_twist.twist.linear.x = max(my_twist.twist.linear.x - 1, -50)
                elif ch == 'a':
                    # 左拐 steer_data: 转向角 -24 ～ 24.0 度
                    my_twist.twist.angular.z = min(my_twist.twist.angular.z + 1, 24)
                elif ch == 'd':
                    my_twist.twist.angular.z = max(my_twist.twist.angular.z - 1, -24)
                elif ch == 'g':
                    # 开始录制
                    my_twist.cl = 1.0
                elif ch == ' ':
                    # 发生越界，需要进行刹车和对当前帧打标签
                    my_twist.twist.linear.x = 0
                    my_twist.cl = -1.0
                elif ch == 'q':
                    exit()
        except Exception as e:
            rospy.logerr(e)
        # 发布消息
        turtle_vel_pub.publish(my_twist)
        rospy.loginfo('publish %0.2f m/s, %0.2f rad/s is CL? %0.0f', my_twist.twist.linear.x, my_twist.twist.angular.z,
                      my_twist.cl)

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
