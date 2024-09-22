import asyncio
from bleak import BleakClient

# Replace with the MAC address of your BLE device
device_mac = "04:A3:16:A9:72:FE"


async def discover_services_and_characteristics():
    async with BleakClient(device_mac) as client:
        services = await client.get_services()
        for service in services:
            print(f"Service UUID: {service.uuid}")
            characteristics = service.characteristics
            for char in characteristics:
                print(f"  Characteristic UUID: {char.uuid}")


# Run the async function to discover services and characteristics
asyncio.run(discover_services_and_characteristics())
