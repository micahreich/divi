#!/usr/bin/env python3
import socket
import rospy
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist


class JoystickTeleop:
    def __init__(self):
        rospy.init_node("joystick_teleop")

        self.max_linear  = rospy.get_param("~max_linear_vel",  1.0)
        self.max_angular = rospy.get_param("~max_angular_vel", 1.0)
        self.linear_axis  = rospy.get_param("~linear_axis",  1)  # left stick Y
        self.angular_axis = rospy.get_param("~angular_axis", 3)  # right stick X

        hostname = socket.gethostname()
        self.angular_sign = -1.0 if hostname == "mreich-nano2" else 1.0

        self.cmd_pub = rospy.Publisher("cmd_vel", Twist, queue_size=1)
        rospy.Subscriber("joy", Joy, self._joy_cb)

    def _joy_cb(self, msg):
        twist = Twist()
        twist.linear.x  = msg.axes[self.linear_axis]  * self.max_linear
        twist.angular.z = msg.axes[self.angular_axis] * self.max_angular * self.angular_sign
        self.cmd_pub.publish(twist)

    def run(self):
        rospy.spin()


if __name__ == "__main__":
    try:
        JoystickTeleop().run()
    except rospy.ROSInterruptException:
        pass
