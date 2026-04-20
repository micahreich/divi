import time
import sys
from roboclaw_driver.roboclaw_3 import Roboclaw

PORT = "/dev/ttyACM0"
BAUD = 38400
ADDRESS = 0x80

rc = Roboclaw(PORT, BAUD)
rc.Open()

def reset_encoders():
    rc.ResetEncoders(ADDRESS)
    print("Encoders reset")

def read_encoders():
    enc1 = rc.ReadEncM1(ADDRESS)
    enc2 = rc.ReadEncM2(ADDRESS)
    return enc1[1], enc2[1]

def set_speed(m1_speed, m2_speed):
    """Speed in encoder counts per second. Negative = reverse."""
    if m1_speed >= 0:
        rc.SpeedM1(ADDRESS, m1_speed)
    else:
        rc.BackwardM1(ADDRESS, abs(m1_speed))

    if m2_speed >= 0:
        rc.SpeedM2(ADDRESS, m2_speed)
    else:
        rc.BackwardM2(ADDRESS, abs(m2_speed))

def stop():
    rc.ForwardM1(ADDRESS, 0)
    rc.ForwardM2(ADDRESS, 0)
    print("Stopped")

def run_speed_test(speed, duration):
    reset_encoders()
    print(f"Running at speed {speed} for {duration}s...")
    set_speed(speed, speed)

    start = time.time()
    while time.time() - start < duration:
        e1, e2 = read_encoders()
        print(f"  M1: {e1}, M2: {e2}", end="\r")
        time.sleep(0.1)

    stop()
    e1, e2 = read_encoders()
    print(f"\nFinal - M1: {e1}, M2: {e2}")

if __name__ == "__main__":
    # Usage: python script.py <speed> <duration>
    # Speed = encoder counts/sec, Duration = seconds
    # Example: python script.py 1000 3
    speed = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    duration = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0

    run_speed_test(speed, duration)