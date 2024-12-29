"""import pywinusb.hid as hid

def list_usb_devices():
    # Get the connected USB devices
    devices = hid.HidDeviceFilter().get_devices()
    for device in devices:
        print(f"Device: {device.device_path}")
        print(f"Device Name: {device.product_name}")
        #print(f"Manufacturer: {device.manufacturer_name}")
        print(f"Vendor ID: {device.vendor_id}")
        print(f"Product ID: {device.product_id}")
        print("-" * 50)

list_usb_devices()

"""
import win32com.client

def list_usb_devices():
    wmi = win32com.client.GetObject("winmgmts:\\\\.\\root\\cimv2")
    usb_devices = wmi.ExecQuery("SELECT * FROM Win32_USBHub")

    query = "SELECT * FROM Win32_PnPEntity WHERE DeviceID LIKE '%{}%'".format("nonesense")
    devices = wmi.ExecQuery(query)
    if not devices.DeviceID:
        print("empty")

    for device in devices:
        print(f"Device Name: {device.DeviceID}")
        print(f"Device Description: {device.Description}")
        print(f"Device PNPDeviceID: {device.PNPDeviceID}")
        print("-" * 50)

list_usb_devices()
