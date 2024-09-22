"""
import matplotlib.pyplot as plt
import serial

# Create empty lists to store data
y_data = []

# Create a function to update the plot
def update_plot():
    # Read data from the serial port
    data = ser.readline().decode('utf8').strip()
    if data:
        print(data)
        cm = int(data.split()[1].strip("cm"))

        # Append data to the list
        y_data.append(cm)

        # Limit the number of data points displayed
        if len(y_data) > 50:
            y_data.pop(0)

        ax.clear()
        ax.bar(range(len(y_data)), y_data)
        ax.set_ylabel('Distance (cm)')
        ax.set_title('Static Distance Plot')

# Set up the Matplotlib figure
fig, ax = plt.subplots()

# Define serial port and baud rate
comport = 'COM3'
baudrate = 115200

# Open the serial port
ser = serial.Serial(comport, baudrate, timeout=0.1)

try:
    while True:
        # Update the plot
        update_plot()
        plt.pause(0.01)

except KeyboardInterrupt:
    pass
finally:
    # Close the serial port
    ser.close()

plt.show()
"""

import serial


def readserial(comport, baudrate):

    ser = serial.Serial(comport, baudrate, timeout=0.1)         # 1/timeout is the frequency at which the port is read

    while True:
        data = ser.readline().decode().strip()
        if data:
            print(data)


if __name__ == '__main__':

    readserial('COM3', 115200)
