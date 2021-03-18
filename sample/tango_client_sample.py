
from tmc.common.tango_client import TangoClient


def testassign_cb(self, event):
    """
    Callback function immediately executed when the asynchronous invoked command returns

    :return: none
    """
    if event.err:
        log = "Error in invoking command" + event.cmd_name + {event.errors}
        self.logger.info(log)
    else:
        log = "Command" + event.cmd_name + "invoked successfully"
        self.logger.info(log)


def testattr_cb(self, event):
    """
    Retrieves the subscribed attribute of a device.

    :return: None
    """
    if event.err:
        log = "Attribute" + event.attr_name + {event.errors}
        self.logger.info(log)
        self.logger.info("Error in subscribing to attribute" )
    else:
        log_msg = f"Attribute event value is : {event.attr_value.value}"
        log = "Attribute" + event.attr_name + "is subscribed successfully"
        self.logger.info(log_msg)
        self.logger.info(log)

def main():
    """
    Runs the tango_client_sample.
    """

    print("Creating main method for tango_client_sample")

    #This is for client object creation. Here, "sys/tg_test/1" is the fqdn of the device.    
    client_sample = TangoClient("sys/tg_test/1")

    #This invokes command on the device server. The command testassign is implemented on server side.
    client_sample.send_command("testassign")
    
    #This invokes command on the device server in asynchronous mode.
    #testassign_cb is the callback function that should be executed after completion of the command execution.
    client_sample.send_command_async("testassign", testassign_cb)

    #This reads the value to the given attribute. The attribute testattr is implemented on server side.
    client_sample.get_attribute("testattr")

    #This writes the value to the given attribute with the value.
    client_sample.set_attribute("testattr", 200)

    #This subscribes to the event of the attribute and return the event id.
    #testattr_cb is the attribute callback function which will be executed after successful attribute calling.
    client_sample.subscribe_attribute("testattr", testattr_cb )

    #This unsubscribes to the event of attribute of the particular event id generated.
    client_sample.unsubscribe_attribute(eventid)

if __name__ == "__main__":
    main()