###########
Change Log
###########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

Added
-----
[0.16.0]
************
* Added sourceOffset attribute to expose commanded offset during calibration scan_id
* Added sdpQueueConnectorFqdn attribute to process the pointing calibration received from SDP queue connector device.
* Removed pointig_offsets and added pointing_cal attribute for Dish Id's SKA001, SKA002, SKA003, SKA004, SKA036, SKA063 and SKA100 in SDP queue connector device.
  
[0.15.6]
************
* Utilised ska-telmodel v1.15.1

[0.15.5]
************
* Added a method **remove_devices** in liveliness probe to allow removal of devices from monitoring list.

[0.15.3]
************
* Introduced dishMode and pointingState attributes on HelperDishLNDevice

[0.15.2]
************
* Updated device availability to be **True** by default

[0.15.0]
************
* Updated Scan command interface to include scan_id as argument
* EndScan command has been added in HelperDishLNDevice
* **scanID** attribute has been introduced in HelperDishDevice

[0.14.0]
************
* Update pytango v9.4.2
* Variable **SetisSubsystemAvailable** is change to **SetSubsystemAvailable**
* .darglint file to accomadate sphinx style rst documentation
* TimeKeeper class added for handling timout functionality
* Input type for **start_tracker_thread** method for param **state_function** is changed from **Callable** to **str**
* **timeout_decorator** and **error_propagation_decorator** added for implementing timeout and error propagation functionalities respectively


Fixed
-----
[0.15.11]
************

* Delay added for MCCS Subarray Configure command

[0.15.10]
************
* Fixed Configure command of HelperDishLNDevice send pointingState and dishMode with delay interval

[0.15.9]
************
* Fixed Scan Command of HelperSubarrayLeafDevice to directly send the ObsState event.

[0.15.8]
************
* Removed duplicate set_change_event calls for the attributes inherited from the base classes
* Utilised Timer thread to simulate pushing of the transitional and final obstate events
* Updated **DeviceInfo** and child classes to implement their own locks

[0.15.7]
************
* Updated Scan Command of HelperSubarrayLeafDevice to introduce a delay in ObsState event received on SubarrayNode.

[0.15.4]
************
* **is_command_allowed** methods for all commands is removed from helper sdp subarray

[0.15.2]
************
* Updated **HelperDishDevice** to add EndScan command to reset **scanID** attribute.

[0.15.1]
************
* Updated **push_command_result** method from the HelperBaseDevice to take correct number of arguments
* The sequence of executing cleanup and **update_task_status** method is reversed in the Tracker Thread

[0.14.0]
************
* Fixed Pylint warnigs
* Fixed docstrings warnings