import serial
import pygame
import sys
import math





SCREEN_WIDTH, SCREEN_HEIGHT = 900, 900
BACKGROUND_COLOR = (255, 255, 255)
ROBOT_PATH_COLOR = (0, 0, 0)
OBSTACLE_COLOR = (255, 0, 0)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SLAM MAP")

robot_x = SCREEN_WIDTH // 2
robot_y = SCREEN_HEIGHT // 2
robot_angle = 0

robot_path = []
obstacles = []


def draw_dot(x, y, color):
    pygame.draw.circle(screen, color, (int(x), int(y)), 1)


robot_forward_distance = 0
robot_backward_distance = 0


def update_robot_position():
    global robot_x, robot_y, robot_forward_distance, robot_backward_distance
    movement = (robot_forward_distance - robot_backward_distance) / 2
    robot_x += movement * math.cos(math.radians(robot_angle))
    robot_y -= movement * math.sin(math.radians(robot_angle))
    robot_path.append((robot_x, robot_y))


def draw_robot():
    pygame.draw.circle(screen, ROBOT_PATH_COLOR, (int(robot_x), int(robot_y)), 10)


def draw_obstacles():
    global obstacles
    prev_x, prev_y = None, None

    for obstacle_x, obstacle_y in obstacles:
        if prev_x is not None:
            distance = math.sqrt((obstacle_x - prev_x) ** 2 + (obstacle_y - prev_y) ** 2)
            angle_diff = abs(robot_angle - math.degrees(math.atan2(obstacle_y - prev_y, obstacle_x - prev_x)))
            if angle_diff <= 2 and distance <= 4:
                pygame.draw.line(screen, ROBOT_PATH_COLOR, (int(prev_x), int(prev_y)),
                                 (int(obstacle_x), int(obstacle_y)),
                                 2)
            else:
                draw_dot(obstacle_x, obstacle_y, OBSTACLE_COLOR)
        prev_x, prev_y = obstacle_x, obstacle_y


def readserial(comport, baudrate):
    ser = serial.Serial(comport, baudrate, timeout=0.1)
    global robot_x, robot_y, robot_forward_distance, robot_backward_distance, robot_angle

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        data = ser.readline().decode().strip()
        if data:
            try:
                parts = data.split()
                if len(parts) == 4:
                    distance, angle, forward_distance, backward_distance = parts
                    distance = int(distance.replace("cm", ""))
                    angle = int(angle.replace("^0", ""))
                    forward_distance = int(forward_distance.replace("cm", ""))
                    backward_distance = int(backward_distance.replace("cm", ""))

                    robot_forward_distance = forward_distance
                    robot_backward_distance = backward_distance
                    robot_angle = angle
                    update_robot_position()

                    distance_to_obstacle = distance
                    obstacle_x = robot_x + distance_to_obstacle * math.cos(math.radians(robot_angle))
                    obstacle_y = robot_y - distance_to_obstacle * math.sin(math.radians(robot_angle))

                    obstacles.append((obstacle_x, obstacle_y))

                    screen.fill(BACKGROUND_COLOR)
                    for x, y in robot_path:
                        draw_dot(x, y, ROBOT_PATH_COLOR)
                    draw_obstacles()
                    draw_robot()
                    draw_dot(robot_x, robot_y, ROBOT_PATH_COLOR)
                    pygame.display.flip()
                else:
                    print("Invalid data format")
            except ValueError:
                print("Invalid data format")


if __name__ == '__main__':
    try:
        readserial('COM3', 115200)
    except KeyboardInterrupt:
        pass

    pygame.quit()
