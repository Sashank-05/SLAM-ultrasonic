import numpy as np
import matplotlib.pyplot as plt
from math import *
import math
import time

import asyncio
import sys

import threading
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

# Taking Initial angle from compass
initial_angle_from_compass = float(input("Enter the inital angle from compass: "))

UART_SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
UART_RX_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
UART_TX_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

LDATA = ""
LDATATMP = ""
LTMP = ""

PACKET = ""

# Function to find the coordinate given distance and angle
def distance_coordinate_finder(current_location, angle_from_compass, distance, distance_number):
    theta = angle_from_compass - initial_angle_from_compass
    print(f'theta = {theta}')
    if distance_number == 1:
        print(f'distance = {distance}, current_location = {current_location}')
        print(f'cos(90-theta) = {cos(radians(90 - 0))}')
        x = round(current_location[0] + distance * (cos(radians(90 - theta))), 2)
        y = current_location[1] + distance * (sin(radians(90 - theta)))
        print(f'x={x},y={y}')
        return (x, y)
    elif distance_number == 2:
        print(f'distance = {distance}, current_location = {current_location}')
        x = round(current_location[0] + distance * (cos(radians(180 - theta))), 2)
        y = round(current_location[1] + distance * (sin(radians(180 - theta))), 2)
        print(f'x={x},y={y}')
        return (x, y)
    elif distance_number == 3:
        print(f'distance = {distance}, current_location = {current_location}')
        x = round(current_location[0] + distance * (cos(radians(270 - theta))), 2)
        y = round(current_location[1] + distance * (sin(radians(270 - theta))), 2)
        print(f'x={x},y={y}')
        return (x, y)
    elif distance_number == 4:
        print(f'distance = {distance}, current_location = {current_location}')
        x = round(current_location[0] + distance * (cos(radians(360 - theta))), 2)
        y = round(current_location[1] + distance * (sin(radians(360 - theta))), 2)
        print(f'x={x},y={y}')
        return (x, y)


def current_loc_coordinate(temp_distance_coordinate_list):
    def intersection_point(line1_coords, line2_coords):
        x1, y1 = line1_coords[0]
        x2, y2 = line1_coords[1]
        x3, y3 = line2_coords[0]
        x4, y4 = line2_coords[1]
        # Calculate the slopes of the lines
        slope1 = (y2 - y1) / (x2 - x1) if x2 != x1 else float('inf')  # Handle vertical lines
        slope2 = (y4 - y3) / (x4 - x3) if x4 != x3 else float('inf')  # Handle vertical lines
        # Check if the lines are parallel
        if slope1 == slope2:
            return None  # Lines are parallel, no intersection
        # Calculate the intersection point
        if slope1 == float('inf'):  # Line 1 is vertical
            x_intersect = x1
            y_intersect = slope2 * (x1 - x3) + y3
        elif slope2 == float('inf'):  # Line 2 is vertical
            x_intersect = x3
            y_intersect = slope1 * (x3 - x1) + y1
        else:
            x_intersect = ((slope1 * x1 - y1) - (slope2 * x3 - y3)) / (slope1 - slope2)
            y_intersect = slope1 * (x_intersect - x1) + y1
        return (x_intersect, y_intersect)

    lined1d3 = [temp_distance_coordinate_list[0], temp_distance_coordinate_list[2]]
    lined2d4 = [temp_distance_coordinate_list[1], temp_distance_coordinate_list[3]]
    return intersection_point(lined1d3, lined2d4)


# new_coordinates finder when it moves at an angle of theta front or back:
def new_coordinates(current_loc_coordinate, theta_degrees, d):
    # Convert angle from degrees to radians
    theta_radians = radians(theta_degrees)
    # Adjust angle if distance is negative
    if d < 0:
        theta_radians += math.pi  # Add 180 degrees
    # Calculate new coordinates
    x1 = current_loc_coordinate[0] + d * cos(theta_radians)
    y1 = current_loc_coordinate[1] + d * sin(theta_radians)
    return (x1, y1)


# Creating a plot to plot
fig, ax = plt.subplots()
ax.set_xlim(-100, 100)
ax.set_ylim(-100, 100)

#canstart = bool(input("Enter if you want to start"))

current_location = [0, 0]
angle_from_compass_to_compare = initial_angle_from_compass
d1prev, d2prev, d3prev, d4prev = 70, 5, 5, 5
permanent_distance_coordinate_list = [distance_coordinate_finder(current_location, 180, d1prev, 1),
                                      distance_coordinate_finder(current_location, 180, d2prev, 2),
                                      distance_coordinate_finder(current_location, 180, d3prev, 3),
                                      distance_coordinate_finder(current_location, 180, d4prev, 4)]

print("Current location:", current_location)


def scanthread():
    global PACKET


    while 1:
        try:
            d1, d2, d3, d4, angle_from_compass = map(int, PACKET.split())
            distance_list = [d1, d2, d3, d4]
        except:
            continue
        ax.clear()
        ax.plot(current_location[0], current_location[1], 'ro', markersize=3)
        for coordinates in permanent_distance_coordinate_list[-4:]:
            ax.plot(coordinates[0], coordinates[1], 'go', markersize=1)




        temp_distance_coordinate_list = []

        if angle_from_compass_to_compare != angle_from_compass:
            current_slam_coordinate = current_location
            # Printing how much degrees the slam has turned
            print(f"The slam has turned an angle of {angle_from_compass - initial_angle_from_compass} degr3ees")
            # Creating a temporary coordinate list for appending the coordinates of each of the distances
            for i in range(len(distance_list)):
                # printing each of the distances
                print(f'd{i + 1} = {distance_list[i]}')
                # converting each of the distances given the angle slam has turned to coordinates with respect to current_location and then adding it into 2 lists
                # temp_distance_coordinate_list and permanent_distance_coordinate_list <-- defined outside the loop contains all the points to be plotted
                coordinate = distance_coordinate_finder(current_slam_coordinate, angle_from_compass, distance_list[i],
                                                        i + 1)
                temp_distance_coordinate_list.append(coordinate)
                permanent_distance_coordinate_list.append(coordinate)
        else:
            # d1d2 line previously should be in the same line as new d1d2 line
            # same for d3d4 line
            if d1prev - d1 > 0:
                print(f"The slam has moved forward towards d1")
                thetad1 = 90 - (angle_from_compass - initial_angle_from_compass)
                current_slam_coordinate = new_coordinates(current_location, thetad1, d1prev - d1)
                permanent_distance_coordinate_list.append(
                    distance_coordinate_finder(current_slam_coordinate, angle_from_compass, d1, 1))
                permanent_distance_coordinate_list.append(
                    distance_coordinate_finder(current_slam_coordinate, angle_from_compass, d2, 2))
                permanent_distance_coordinate_list.append(
                    distance_coordinate_finder(current_slam_coordinate, angle_from_compass, d3, 3))
                permanent_distance_coordinate_list.append(
                    distance_coordinate_finder(current_slam_coordinate, angle_from_compass, d4, 4))
            elif d1prev - d1 < 0:
                print(f"The slam has moved backward towards d3")
                thetad3 = 270 - (angle_from_compass - initial_angle_from_compass)
                current_slam_coordinate = new_coordinates(current_location, thetad3, d1prev - d1)
                permanent_distance_coordinate_list.append(
                    distance_coordinate_finder(current_slam_coordinate, angle_from_compass, d1, 1))
                permanent_distance_coordinate_list.append(
                    distance_coordinate_finder(current_slam_coordinate, angle_from_compass, d2, 2))
                permanent_distance_coordinate_list.append(
                    distance_coordinate_finder(current_slam_coordinate, angle_from_compass, d3, 3))
                permanent_distance_coordinate_list.append(
                    distance_coordinate_finder(current_slam_coordinate, angle_from_compass, d4, 4))
            elif d2prev - d2 > 0:
                print(f"The slam has moved left towards d2")
                thetad2 = 180 - (angle_from_compass - initial_angle_from_compass)
                current_slam_coordinate = new_coordinates(current_location, thetad2, d2prev - d2)
                permanent_distance_coordinate_list.append(
                    distance_coordinate_finder(current_slam_coordinate, angle_from_compass, d1, 1))
                permanent_distance_coordinate_list.append(
                    distance_coordinate_finder(current_slam_coordinate, angle_from_compass, d2, 2))
                permanent_distance_coordinate_list.append(
                    distance_coordinate_finder(current_slam_coordinate, angle_from_compass, d3, 3))
                permanent_distance_coordinate_list.append(
                    distance_coordinate_finder(current_slam_coordinate, angle_from_compass, d4, 4))
            elif d2prev - d2 < 0:
                print(f"The slam has moved right towards d4")
                thetad4 = 360 - (angle_from_compass - initial_angle_from_compass)
                current_slam_coordinate = new_coordinates(current_location, thetad4, d2prev - d2)
                permanent_distance_coordinate_list.append(
                    distance_coordinate_finder(current_slam_coordinate, angle_from_compass, d1, 1))
                permanent_distance_coordinate_list.append(
                    distance_coordinate_finder(current_slam_coordinate, angle_from_compass, d2, 2))
                permanent_distance_coordinate_list.append(
                    distance_coordinate_finder(current_slam_coordinate, angle_from_compass, d3, 3))
                permanent_distance_coordinate_list.append(
                    distance_coordinate_finder(current_slam_coordinate, angle_from_compass, d4, 4))
        # taking the 4 last coordinate values
        d1prev, d2prev, d3prev, d4prev = d1, d2, d3, d4

        current_location[0] = current_slam_coordinate[0]
        current_location[1] = current_slam_coordinate[1]

        print(f'slams current loc = {current_location}')
        print(f'permanent_distance_coordinate_list = {permanent_distance_coordinate_list}')

        plt.pause(0.1)

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
    pygame_thread = threading.Thread(target=scanthread)
    pygame_thread.start()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(uart_terminal())
