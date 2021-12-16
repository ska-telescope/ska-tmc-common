
from tmc.common.tango_client import TangoClient


def devdouble_cb(event):
    """
    Callback function when the command execution is completed on server side.

    :return: None
    """
    print("Inside command callback method.")
    print(f"Event received from device: {event}")


def ampli_cb(event):
    """
    Callback function to process the event received from device server.

    :return: None
    """
    print("Inside attribute callback method.")
    print(f"Event received from device: {event}")


def main():
    """
    Main method of the sample Tango client.
    """

    #This is for client object creation. Here, "sys/tg_test/1" is the fqdn of the device.
    print("Creating client of TangoTest device.")
    client_sample = TangoClient("sys/tg_test/1")

    #This invokes command on the device server in synchronous mode.
    print("Sending command in synchronous mode.")
    client_sample.send_command("DevDouble", 20)
    
    #This invokes command on the device server in asynchronous mode.
    #devdouble_cb is the callback function that gets executed after completion of the command execution.
    print("Sending command in asynchronous mode.")
    client_sample.send_command_async("DevDouble", 40, devdouble_cb)

    #This reads the value to the given attribute.
    print("Reading attribute.")
    print(client_sample.get_attribute("ampli"))

    #This writes the value to the given attribute with the value.
    print("Writing value to attribute.")
    client_sample.set_attribute("ampli", 100)
    print(client_sample.get_attribute("ampli"))

    #This subscribes to the event of the attribute and return the event id.
    #ampli_cb is the attribute callback function which will be executed after successful attribute calling.
    print("Subscribing attribute change event.")
    eventid = client_sample.subscribe_attribute("ampli", ampli_cb )

    #This unsubscribes to the event of attribute of the particular event id generated.
    print("Unsubscribing attribute change event.")
    client_sample.unsubscribe_attribute(eventid)

if __name__ == "__main__":
    main()