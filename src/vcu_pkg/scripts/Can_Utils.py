from time import sleep

import cantools
from pprint import pprint
import can
from functools import reduce
from geometry_msgs.msg import Twist

db = cantools.db.load_file('/home/swucar/Desktop/swu-car/src/vcu_pkg/scripts/VCU_Auto_CAN.dbc')

can_bus = can.interface.Bus('can0', bustype='socketcan', bitrate=500000)

# pprint(db.messages)

gearCmd_message = db.get_message_by_name('Auto_GearCmd')  # 档位 2：后退， 3：空档， 4：前进
steeringCmd_message = db.get_message_by_name('Auto_SteeringCmd')  # 转向角 {-90 左转， 89.954775 右转} 车辆实际最大转向角是 -24 ～ 24
driveCmd_message = db.get_message_by_name('Auto_DriveCmd')  #
brakingCmd_message = db.get_message_by_name('Auto_BrakingCmd')
parkingCmd_message = db.get_message_by_name('Auto_ParkingCmd')


# pprint(gearCmd_message.signals)
# pprint(steeringCmd_message.signals)
# pprint(driveCmd_message.signals)
# pprint(brakingCmd_message.signals)
# pprint(parkingCmd_message.signals)

class CanUtil:
    def __init__(self):
        self.alive_id = 0

    @staticmethod
    # 计算一个 bytes 数据的异或值，这个是后面计算校验码用的
    def check_sum(bytes_list):
        return reduce(lambda x, y: x ^ y, bytes_list)

    def update_alive_id(self):
        self.alive_id = (self.alive_id + 1) % 16

    # 刹车
    def brake(self):
        pass

    # 驻车
    def park(self):
        pass

    # def drive(self, twist, braking=0, parking=0):
    def drive(self, twist):
        if twist.linear.x < 0:
            # 倒车
            self.send_can(2, twist.angular.z, -twist.linear.x, 0, 0)
        else:
            # 前进
            self.send_can(4, twist.angular.z, twist.linear.x, 0, 0)

    '''
    # gear_data: 档位 2：后退， 3：空档， 4：前进
    # steer_data: 转向角 -24 ～ 24.0
    # speed_data: 速度 -5.0 ～ 5.0
    # brake_data: 刹车 0 ～ 1.0
    # park_data: 驻车 0 | 1 { 0：松开电磁抱闸， 1：电磁抱闸 }
    '''

    def send_can(self, gear_data=3, steer_data=0, speed_data=0, brake_data=0, park_data=0):
        # 档位 2：后退， 3：空档， 4：前进
        auto_gear_cmd_data = gearCmd_message.encode({'Auto_GearCmd_GearEnable': 1, 'Auto_GearCmd_TargetGear': gear_data,
                                                     'Auto_GearCmd_AliveCounter': self.alive_id,
                                                     'Auto_GearCmd_CheckSum': 0})
        auto_gear_cmd_data = gearCmd_message.encode({'Auto_GearCmd_GearEnable': 1, 'Auto_GearCmd_TargetGear': gear_data,
                                                     'Auto_GearCmd_AliveCounter': self.alive_id,
                                                     'Auto_GearCmd_CheckSum': CanUtil.check_sum(auto_gear_cmd_data)})
        auto_gear_cmd_data_message = can.Message(arbitration_id=gearCmd_message.frame_id, data=auto_gear_cmd_data)

        # 转向角 {24.0 左转， -24.0 右转}
        steering_cmd_data = steeringCmd_message.encode(
            {'Auto_SteeringCmd_SteeringEnable': 1, 'Auto_SteeringCmd_TargetAngle': steer_data,
             'Auto_SteeringCmd_SteeringSpeed': 0,
             'Auto_SteeringCmd_AliveCounter': self.alive_id,
             'Auto_SteeringCmd_CheckSum': 0})
        steering_cmd_data = steeringCmd_message.encode(
            {'Auto_SteeringCmd_SteeringEnable': 1, 'Auto_SteeringCmd_TargetAngle': steer_data,
             'Auto_SteeringCmd_SteeringSpeed': 0,
             'Auto_SteeringCmd_AliveCounter': self.alive_id,
             'Auto_SteeringCmd_CheckSum': CanUtil.check_sum(steering_cmd_data)})
        steering_cmd_data_message = can.Message(arbitration_id=steeringCmd_message.frame_id, data=steering_cmd_data)

        # 车速  { 0 ～ 5 m/s ，大于 5 时 也就是等于 5 }
        drive_cmd_data = driveCmd_message.encode(
            {'Auto_DriveCmd_DriveEnable': 1, 'Auto_DriveCmd_TargetVelocity': 0.1 * speed_data,
             'Auto_DriveCmd_AliveCounter': self.alive_id,
             'Auto_DriveCmd_CheckSum': 0})
        drive_cmd_data = driveCmd_message.encode(
            {'Auto_DriveCmd_DriveEnable': 1, 'Auto_DriveCmd_TargetVelocity': 0.1 * speed_data,
             'Auto_DriveCmd_AliveCounter': self.alive_id,
             'Auto_DriveCmd_CheckSum': CanUtil.check_sum(drive_cmd_data)})
        drive_cmd_data_message = can.Message(arbitration_id=driveCmd_message.frame_id, data=drive_cmd_data)

        # 刹车 { 0 ～ 99.6}
        braking_cmd_data = brakingCmd_message.encode(
            {'Auto_BrakingCmd_BrakingEnable': 1, 'Auto_BrakingCmdTargetPedalPos': brake_data * 99.6,
             'Auto_BrakingCmd_AliveCounter': self.alive_id,
             'Auto_BrakingCmd_CheckSum': 0})
        braking_cmd_data = brakingCmd_message.encode(
            {'Auto_BrakingCmd_BrakingEnable': 1, 'Auto_BrakingCmdTargetPedalPos': brake_data * 99.6,
             'Auto_BrakingCmd_AliveCounter': self.alive_id,
             'Auto_BrakingCmd_CheckSum': CanUtil.check_sum(braking_cmd_data)})
        braking_cmd_data_message = can.Message(arbitration_id=brakingCmd_message.frame_id, data=braking_cmd_data)

        # 驻车 { 0：松开电磁抱闸， 1：电磁抱闸 }
        parking_cmd_data = parkingCmd_message.encode(
            {'Auto_ParkingCmd_ParkingEnable': 1, 'Auto_ParkingCmd_ParkingRequest': park_data,
             'Auto_ParkingCmd_AliveCounter': self.alive_id,
             'Auto_ParkingCmd_CheckSum': 0})
        parking_cmd_data = parkingCmd_message.encode(
            {'Auto_ParkingCmd_ParkingEnable': 1, 'Auto_ParkingCmd_ParkingRequest': park_data,
             'Auto_ParkingCmd_AliveCounter': self.alive_id,
             'Auto_ParkingCmd_CheckSum': CanUtil.check_sum(parking_cmd_data)})
        parking_cmd_data_message = can.Message(arbitration_id=parkingCmd_message.frame_id, data=parking_cmd_data)

        can_bus.send(auto_gear_cmd_data_message)
        can_bus.send(steering_cmd_data_message)
        can_bus.send(drive_cmd_data_message)
        can_bus.send(braking_cmd_data_message)
        can_bus.send(parking_cmd_data_message)
        print('发送-----', self.alive_id, drive_cmd_data_message)
        self.update_alive_id()


if __name__ == '__main__':
    t = Twist()
    t.linear.x = 1
    t.angular.z = 0.5
    canu = CanUtil()
    for i in range(120):
        canu.drive(t)
        sleep(0.02)
