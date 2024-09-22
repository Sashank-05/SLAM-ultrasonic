import asyncio
import sys
import threading
from itertools import count, takewhile
import time
import random

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

# BLE CONFIG
UART_SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
UART_RX_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
UART_TX_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

LDATA = ""
LDATATMP = ""
LTMP = ""

PACKET = ""


def sliced(data: bytes, n: int):
    return takewhile(len, (data[i: i + n] for i in count(0, n)))


def render_pygame():
    # we import here because pygame causes problem with threading if imported on main thread
    import pygame
    import math
    import matplotlib.pyplot as plt

    pygame.init()
    pygame.display.set_caption("SLAM Mapping")
    screen = pygame.display.set_mode((1200, 860))
    rover_color = (0, 0, 0)  # Change to black
    rover_size = (11, 18)
    rover_orientation = None
    rover_x, rover_y = 1200 / 2, 860 / 2  # Example initial position
    # Assuming you have wall length and width
    wall_length = 1000
    wall_width = 750
    clock = pygame.time.Clock()
    # Set up Pygame window
    width, height = 1200, 900
    # Initialize lists to store history
    rover_history = [(rover_x, rover_y)]
    front_dot_history = []
    left_dot_history = []
    right_dot_history = []
    fake_dot_history = []

    U_hat = 0
    K = 0

    def kalman(U):
        """
        some sort of kalman filter
        :param U:
        :return:
        """
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

    def plot_graphs(data, kalman_data):
        plt.clf()
        plt.plot(data, label='Raw Data')
        plt.plot(kalman_data, label='Kalman Filter Output')
        plt.legend()
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.title('Kalman Filter Example')
        plt.pause(0.01)  # Add a short pause to update the plot
        plt.show(block=False)

    while True:
        screen.fill((255, 255, 255))  # Clear the screen with white

        data = PACKET.split()

        if PACKET == "TERMINATE":
            sys.exit(-1)

        if data == [] or data is None:
            # print("nothing to process", end="\r")
            continue

        if data[0] == "MF":  # simulate rover "move front"
            #  rover_x += int(4 * 3 * math.cos(math.radians(rover_orientation)))
            # rover_y -= int(4 * 3 * math.sin(math.radians(rover_orientation)))
            # rotated_rover_rect = rotated_rover_surface.get_rect(center=(rover_x, rover_y))
            # screen.blit(rotated_rover_surface, rotated_rover_rect.topleft)
            continue

        try:
            d1, d2, d3, d4, compass, deg = map(int, data)

        except Exception as e:
            #  print("Exception ", e)
            continue
        # Create the rover surface and rotate it
        if rover_orientation is None:
            rover_orientation = compass
        rover_surface = pygame.Surface(rover_size)
        rover_surface.fill(rover_color)
        rotated_rover_surface = pygame.transform.rotate(rover_surface, -rover_orientation)
        rotated_rover_rect = rotated_rover_surface.get_rect(center=(rover_x, rover_y))
        screen.blit(rotated_rover_surface, rotated_rover_rect.topleft)
        rover_orientation = compass
        # kalman_d1 = kalman(d1)
        # kalman_d2 = kalman(d2)
        # kalman_d3 = kalman(d3)

        # plot_graphs([d1, d2, d3], [kalman_d1, kalman_d2, kalman_d3])
        rover_history.append((rover_x, rover_y))

        # bruh this is such a waste of time what even is this lmao

        front_dot = (
            rover_x + int(d1 * 100 * math.cos(math.radians(compass))),
            rover_y - int(d1 * 100 * math.sin(math.radians(compass)))
        )
        left_dot = (
            rover_x + int(d2 * 100 * math.cos(math.radians(compass - 90))),
            rover_y - int(d2 * 100 * math.sin(math.radians(compass - 90)))
        )
        right_dot = (
            rover_x + int(d3 * 100 * math.cos(math.radians(compass + 90))),
            rover_y - int(d3 * 100 * math.sin(math.radians(compass + 90)))
        )

        # Update dot histories
        front_dot_history.append(front_dot)
        left_dot_history.append(left_dot)
        right_dot_history.append(right_dot)

        # Draw history
        for point in rover_history:
            pygame.draw.circle(screen, rover_color, (int(point[0]), int(point[1])), 1)

        for point in front_dot_history + left_dot_history + right_dot_history:
            pygame.draw.circle(screen, (255, 0, 0), (int(point[0]), int(point[1])), 1)

        # pygame.draw.rect(screen, (0, 0, 0),
        #      (width // 2 - wall_length // 2, height // 2 - wall_width // 2, wall_length, wall_width), 1)

        # Introduce fake dots on the "wall"
        for i in range(random.randint(0, 25)):  # Adjust the number of points as needed
            fraction = i / 9.0
            fake_dot = (
                width // 2 - wall_length // 2 + int(random.randrange(0, wall_length) * fraction),
                height // 2 - wall_width // 2
            )
            pygame.draw.circle(screen, (255, 0, 0), fake_dot, 2)
            fake_dot_history.append(fake_dot)

            fake_dot = (
                width // 2 - wall_length // 2 + int(random.randrange(0, wall_length) * fraction),
                height // 2 + wall_width // 2
            )
            pygame.draw.circle(screen, (255, 0, 0), fake_dot, 2)
            fake_dot_history.append(fake_dot)
        pygame.display.flip()  # Update the display
        clock.tick(1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()


async def uart_terminal():
    global LDATA, LDATATMP, PACKET

    def match_nus_uuid(device: BLEDevice, adv: AdvertisementData):
        return UART_SERVICE_UUID.lower() in adv.service_uuids

    device = await BleakScanner.find_device_by_filter(match_nus_uuid)

    if device is None:
        print("No matching device found. Edit match_nus_uuid() if needed.")
        PACKET="TERMINATE"


    async def handle_disconnect(_: BleakClient):
        print("Rover has disconnected. Goodbye!")
        for task in asyncio.all_tasks():
            task.cancel()

    async def handle_rx(_: BleakGATTCharacteristic, dat: bytearray):
        global LDATA, LDATATMP, PACKET
        dat = dat.decode('utf8')
        if "MF" in dat:
            dat = dat.replace("MF", "")
        # print(dat)
        if dat[-1] == "\n":
            PACKET = LDATA + dat[:-1]
            if PACKET.endswith("MF\n"):
                PACKET.removesuffix("MF\n")
            print(PACKET)
        else:
            LDATA = dat

    async with BleakClient(device, disconnected_callback=handle_disconnect) as client:
        await client.start_notify(UART_TX_CHAR_UUID, handle_rx)
        print("Connected to BLE!\nType to send anything\n")

        loop = asyncio.get_running_loop()
        nus = client.services.get_service(UART_SERVICE_UUID)
        rx_char = nus.get_characteristic(UART_RX_CHAR_UUID)

        await client.write_gatt_char(rx_char, b"yes", response=False)

        while True:
            data = await loop.run_in_executor(None, sys.stdin.buffer.readline)
            if not data:
                break

            for s in sliced(data, rx_char.max_write_without_response_size):
                await client.write_gatt_char(rx_char, s, response=False)
            print("Sent:", data)


if __name__ == "__main__":
    pygame_thread = threading.Thread(target=render_pygame)
    pygame_thread.start()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(uart_terminal())
