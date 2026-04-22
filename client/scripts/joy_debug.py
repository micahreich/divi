import pygame

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No joystick found")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Connected: {joystick.get_name()}")

while True:
    pygame.event.pump()
        
    print(f"Left stick - X: {joystick.get_axis(0):.3f}, Y: {joystick.get_axis(1):.3f}", end=" | ")
    print(f"Right stick - X: {joystick.get_axis(2):.3f}, Y: {joystick.get_axis(3):.3f}", end="\r")