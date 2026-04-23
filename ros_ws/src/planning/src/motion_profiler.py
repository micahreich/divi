#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist


class MotionProfiler:
    """
    Jerk-limited S-curve velocity smoother.

    Sits between raw joystick cmd_vel_raw and the motor driver cmd_vel.
    Both linear and angular axes are independently jerk- and accel-limited,
    producing smooth S-curve transitions that prevent sudden impulses from
    tipping the robot.

    Profile per axis at each timestep dt:
      1. desired_accel = K * (target - current_vel), clamped to [-max_accel, max_accel]
      2. delta_accel   = clamp(desired_accel - current_accel, ±max_jerk * dt)
      3. current_accel += delta_accel
      4. current_vel   += current_accel * dt, clamped to [-max_vel, max_vel]

    Params
    ------
    ~max_linear_vel    (float, default 1.0)  m/s
    ~max_angular_vel   (float, default 1.0)  rad/s
    ~max_linear_accel  (float, default 0.4)  m/s^2
    ~max_angular_accel (float, default 0.6)  rad/s^2
    ~max_linear_jerk   (float, default 0.8)  m/s^3   — lower = smoother ramp-up
    ~max_angular_jerk  (float, default 1.2)  rad/s^3
    ~rate              (int,   default 50)   Hz
    """

    def __init__(self):
        rospy.init_node("motion_profiler")

        self.max_lin_vel    = rospy.get_param("~max_linear_vel",    1.0)
        self.max_ang_vel    = rospy.get_param("~max_angular_vel",   1.0)
        self.max_lin_acc    = rospy.get_param("~max_linear_accel",  0.4)
        self.max_ang_acc    = rospy.get_param("~max_angular_accel", 0.6)
        self.max_lin_jerk   = rospy.get_param("~max_linear_jerk",   0.8)
        self.max_ang_jerk   = rospy.get_param("~max_angular_jerk",  1.2)
        self.lin_deadband   = rospy.get_param("~linear_deadband",   0.05)
        self.ang_deadband   = rospy.get_param("~angular_deadband",  0.05)
        self.rate_hz        = int(rospy.get_param("~rate", 50))

        # State
        self.target_lin = 0.0
        self.target_ang = 0.0
        self.lin_vel    = 0.0
        self.ang_vel    = 0.0
        self.lin_acc    = 0.0
        self.ang_acc    = 0.0

        self.cmd_pub = rospy.Publisher("cmd_vel", Twist, queue_size=1)
        rospy.Subscriber("cmd_vel_raw", Twist, self._raw_cb)

    @staticmethod
    def _apply_deadband(value, deadband, max_val):
        # Normalize to [-1, 1], apply deadband with rescaling so there's no
        # jump at the deadband edge, then scale back to velocity units.
        norm = max(-1.0, min(1.0, value / max_val)) if max_val > 0 else 0.0
        if abs(norm) < deadband:
            return 0.0
        sign = 1.0 if norm > 0 else -1.0
        rescaled = sign * (abs(norm) - deadband) / (1.0 - deadband)
        return rescaled * max_val

    def _raw_cb(self, msg):
        self.target_lin = self._apply_deadband(msg.linear.x,  self.lin_deadband, self.max_lin_vel)
        self.target_ang = self._apply_deadband(msg.angular.z, self.ang_deadband, self.max_ang_vel)

    @staticmethod
    def _step(vel, acc, target, max_vel, max_acc, max_jerk, dt):
        # High gain so we use full accel when error is large (bang-bang-like)
        # but proportionally decelerate as we close in on the target.
        K = 15.0
        desired_acc = max(-max_acc, min(max_acc, K * (target - vel)))

        # Jerk-limit: acceleration may only change by max_jerk * dt per step
        max_da = max_jerk * dt
        acc = acc + max(-max_da, min(max_da, desired_acc - acc))

        new_vel = max(-max_vel, min(max_vel, vel + acc * dt))

        # If this step crossed the target, snap to it and clear accumulated
        # acceleration so it cannot carry through and cause overshoot/reverse creep.
        if (vel - target) * (new_vel - target) < 0:
            return target, 0.0

        return new_vel, acc

    def run(self):
        rate = rospy.Rate(self.rate_hz)
        last = rospy.Time.now()

        while not rospy.is_shutdown():
            now = rospy.Time.now()
            dt = (now - last).to_sec()
            last = now

            if 0 < dt <= 0.5:
                self.lin_vel, self.lin_acc = self._step(
                    self.lin_vel, self.lin_acc, self.target_lin,
                    self.max_lin_vel, self.max_lin_acc, self.max_lin_jerk, dt)
                self.ang_vel, self.ang_acc = self._step(
                    self.ang_vel, self.ang_acc, self.target_ang,
                    self.max_ang_vel, self.max_ang_acc, self.max_ang_jerk, dt)

                msg = Twist()
                msg.linear.x  = self.lin_vel
                msg.angular.z = self.ang_vel
                self.cmd_pub.publish(msg)

            rate.sleep()


if __name__ == "__main__":
    try:
        MotionProfiler().run()
    except rospy.ROSInterruptException:
        pass
