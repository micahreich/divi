import pygame
import roslibpy
import time
import threading

JETSON_IP_1 = "mreich-nano1"
JETSON_IP_2 = "mreich-nano2"
JETSON_PORT = 9090
PUBLISH_RATE_HZ = 20

JOY_TOPIC = "/joy"

# Button indices (0-indexed); adjust for your controller
BUTTON_A = 1   # toggles IP1-only mode
BUTTON_B = 2   # toggles IP2-only mode

MODE_DUAL = "dual"
MODE_IP1  = "ip1_only"
MODE_IP2  = "ip2_only"

MODE_LABELS = {
    MODE_DUAL: f"DUAL ({JETSON_IP_1} + {JETSON_IP_2})",
    MODE_IP1:  f"IP1 only ({JETSON_IP_1})",
    MODE_IP2:  f"IP2 only ({JETSON_IP_2})",
}


def connect_clients(hosts, port, timeout=5):
    results = [None] * len(hosts)

    def worker(i, host):
        client = roslibpy.Ros(host=host, port=port)
        try:
            client.run(timeout=timeout)
            print(f"Connected to ROS at {host}:{port}")
            results[i] = client
        except Exception as e:
            print(f"Warning: could not connect to {host}:{port} — {e}")

    threads = [threading.Thread(target=worker, args=(i, h), daemon=True)
               for i, h in enumerate(hosts)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout + 2)
    return results


def make_joy_msg(joystick):
    return {
        'header': {
            'stamp': {'secs': int(time.time()), 'nsecs': 0},
            'frame_id': ''
        },
        'axes':    [joystick.get_axis(i)   for i in range(joystick.get_numaxes())],
        'buttons': [joystick.get_button(i) for i in range(joystick.get_numbuttons())],
    }


def make_empty_joy_msg(joystick):
    return {
        'header': {
            'stamp': {'secs': int(time.time()), 'nsecs': 0},
            'frame_id': ''
        },
        'axes':    [0.0] * joystick.get_numaxes(),
        'buttons': [0]   * joystick.get_numbuttons(),
    }


def safe_publish(topic, msg):
    if topic is not None:
        topic.publish(roslibpy.Message(msg))


def main():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No joystick found")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Joystick: {joystick.get_name()}")

    client1, client2 = connect_clients([JETSON_IP_1, JETSON_IP_2], JETSON_PORT)

    if client1 is None and client2 is None:
        print("Could not connect to any ROS host, exiting.")
        pygame.quit()
        return

    topic1 = roslibpy.Topic(client1, JOY_TOPIC, 'sensor_msgs/Joy') if client1 else None
    topic2 = roslibpy.Topic(client2, JOY_TOPIC, 'sensor_msgs/Joy') if client2 else None

    mode = MODE_DUAL
    print(f"Mode: {MODE_LABELS[mode]}  |  [A] = IP1 only  [B] = IP2 only  (press again to return to dual)")

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == BUTTON_A:
                        mode = MODE_IP1 if mode != MODE_IP1 else MODE_DUAL
                        print(f"Mode: {MODE_LABELS[mode]}")
                    elif event.button == BUTTON_B:
                        mode = MODE_IP2 if mode != MODE_IP2 else MODE_DUAL
                        print(f"Mode: {MODE_LABELS[mode]}")

            ip1_active = mode in (MODE_DUAL, MODE_IP1)
            ip2_active = mode in (MODE_DUAL, MODE_IP2)

            live_msg  = make_joy_msg(joystick)
            empty_msg = make_empty_joy_msg(joystick)

            safe_publish(topic1, live_msg  if ip1_active else empty_msg)
            safe_publish(topic2, live_msg  if ip2_active else empty_msg)

            time.sleep(1.0 / PUBLISH_RATE_HZ)

    except KeyboardInterrupt:
        pass
    finally:
        for topic in (topic1, topic2):
            if topic:
                topic.unadvertise()
        for client in (client1, client2):
            if client:
                client.terminate()
        pygame.quit()


if __name__ == "__main__":
    main()
