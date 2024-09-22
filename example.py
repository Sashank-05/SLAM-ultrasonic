import tkinter
import matplotlib
import matplotlib.pyplot as plt
from threading import Thread

plt.switch_backend('qt5agg')
import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

x_values = []
y_values = []
dx_values = []
dy_values = []

# Set up the plots
fig, (ax1, ax2) = plt.subplots(2, 1)

# Set the titles and labels for the first plot
ax1.set_title('X and Y Values')
ax1.set_xlabel('Time')
ax1.set_ylabel('Value')

# Set the titles and labels for the second plot
ax2.set_title('kalman filtered values')
ax2.set_xlabel('Time')
ax2.set_ylabel('Value')
time_variable = 0
# Window dimensions
width, height = 1100, 900
window = pygame.display.set_mode((width, height))  # , pygame.FULLSCREEN)
pygame.display.set_caption('All readings combined')

# Define room dimensions (length and width)
room_length, room_width = 1000, 750

# Define map corners based on room dimensions
map_corners = [(50, 50), (50 + room_length, 50), (50 + room_length, 50 + room_width), (50, 50 + room_width)]

# Generate random noisy points in a square formation with noise
num_side_points = 90  # Number of points on each side of the square
side_length = room_length + room_width  # Length of the square side
noise_amount = 15  # Maximum deviation for noise

# Create square formation with noise
noisy_points = []
for i in range(100):
    noisy_points.append(
        (random.randint(map_corners[0][0], map_corners[2][0]), random.randint(map_corners[1][1], map_corners[2][1])))

for i in range(num_side_points):
    x = map_corners[0][0] + i * (side_length / (num_side_points - 1))
    noisy_points.append((x, map_corners[0][1]))
    noisy_points.append((x, map_corners[2][1]))

    y = map_corners[0][1] + i * (side_length / (num_side_points - 1))
    noisy_points.append((map_corners[0][0], y))
    noisy_points.append((map_corners[1][0], y))

# Introduce noise to the points
noisy_points = [
    (x + random.randint(random.choice((-1, -1)) * noise_amount, noise_amount),
     y + random.randint(random.choice((-1, 1, -1, -1, -1, -1, -1)) * noise_amount, noise_amount))
    for x, y in noisy_points]

# Virtual rover parameters
rover_pos = [100, 100]  # Initial position of the virtual rover
rover_speed = 2  # Speed of the virtual rover
point_increment = 0.1  # Increment for updating noisy point positions

clock = pygame.time.Clock()


def kalman(U):
    R = 40
    H = 1.00
    Q = 10

    global P, U_hat  # Make P and U_hat global variables
    P = 0 if 'P' not in globals() else P  # Initialize P if not defined yet
    U_hat = 0 if 'U_hat' not in globals() else U_hat  # Initialize U_hat if not defined yet

    K = P * H / (H * P * H + R)
    U_hat += K * (U - H * U_hat)
    P = (1 - K * H) * P + Q

    return U_hat


# Pygame loop
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    window.fill((255, 255, 255))  # White background

    # Draw the map
    pygame.draw.polygon(window, (0, 0, 0), map_corners, 1)

    # Move the virtual rover
    rover_pos[0] += rover_speed
    if rover_pos[0] > map_corners[1][0]:
        rover_pos[0] = map_corners[0][0]

    # Update noisy point positions gradually
    # Introduce noise to the lines directly
    noisy_points = []
    for i in range(60):
        x = random.uniform(map_corners[0][0], map_corners[2][0])
        y = random.uniform(map_corners[1][1], map_corners[2][1])
        noisy_points.append((x + random.uniform(-noise_amount, noise_amount),
                             y + random.uniform(-noise_amount, noise_amount)))

    for i in range(num_side_points):
        x = map_corners[0][0] + i * (side_length / (num_side_points - 1))
        noisy_points.append((x + random.uniform(-noise_amount, noise_amount),
                             map_corners[0][1] + random.uniform(-noise_amount, noise_amount)))
        noisy_points.append((x + random.uniform(-noise_amount, noise_amount),
                             map_corners[2][1] + random.uniform(-noise_amount, noise_amount)))

        y = map_corners[0][1] + i * (side_length / (num_side_points - 1))
        noisy_points.append((map_corners[0][0] + random.uniform(-noise_amount, noise_amount),
                             y + random.uniform(-noise_amount, noise_amount)))
        noisy_points.append((map_corners[1][0] + random.uniform(-noise_amount, noise_amount),
                             y + random.uniform(-noise_amount, noise_amount)))

    # Draw noisy points
    for point in noisy_points:
        pygame.draw.circle(window, (255, 0, 0), (int(point[0]), int(point[1])), 1)
        dx = kalman(point[0])
        dy = kalman(point[1])

        x_values.append(point[0])
        y_values.append(point[1])
        dx_values.append(dx)
        dy_values.append(dy)
    ax1.plot(x_values, label='X')
    ax1.plot(y_values, label='Y')
    ax1.legend()

    ax2.plot(dx_values, label='kX')
    ax2.plot(dy_values, label='kY')
    ax2.legend()
    time_variable += 1

    if len(x_values) > 10:
        x_values.pop(0)
        y_values.pop(0)
        dx_values.pop(0)
        dy_values.pop(0)

    pygame.display.update()
    plt.show()
    clock.tick(0.4)  # Set the frame rate to 30 frames per second
    num_side_points += 20
    if len(noisy_points) > 2500:
        noisy_points = []
    if num_side_points > 450:
        num_side_points = 200
