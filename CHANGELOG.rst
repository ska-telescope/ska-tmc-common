###########
Change Log
###########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

Added
-----
[0.17.2]
*********
* Updated ska-telmodel v.1.17.0 which includes OET-TMC low
  Assignresources and low Configure schema
* Included Base class v.1.0.0 updates.

[0.16.9]
***********
* Utilised ska-telmodel v.1.17.0 which includes OET-TMC low
  Assignresources and low Configure schema.

[0.16.4]
***********
* Added SdpQueueConnectorDeviceInfo class to hold SDP queue connector device information.

[0.16.2]
************
* Added Track command in dish master helper device.
* Updated TrackLoadStaticOff in dish master helper device to include command Id changes.

[0.16.0]
************
* Added sourceOffset attribute to expose commanded offset during calibration scan.
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
[0.17.11]
* Fixed the issue of mock objects getting created in HelperAdapterFactory for every device in unittest cases

[0.17.10]
* Update logger statements
* Added new class logManager for managing repetitive logs

[0.17.9]
* Update TelModel version to 1.18.2 

[0.17.8]
* Allows any version of katpoint above **1.0a2**

[0.17.7]
* Fixed the helper dish device achievedPointing attribute to give timestamp in TAI with SKA Epoch.

[0.17.6]
* Added delay for LongRunningCommandResult attribute in mccs master leaf node.

[0.17.5]
***********
* Utilised ska-telmodel v.1.18.1. which includes fix for jones key in low configure schema
* Includes base classes upgrade changes.

[0.16.10]
***********
* Utilised latest ska-telmodel which includes fix for jones key in low configure schema

[0.17.4]
* TelModel version now can be anywhere between **1.17.1** and **2.0.0**

[0.17.3]
* Fixed helper mccs controller device timeout for allocate command.

[0.17.1]
* Fixed change event for dish leaf node and dish device

[0.17.0]
*********
* **BaseClasses** version updated to **1.0.0**
* **PyTango** version updated to **9.5.0**
* Helper Devices updated to send the correct format of **LongRunningCommandResult** events - **(unique_id, (ResultCode.OK, message))**
* The result sent through **update_task_status** method from **track_and_update_command_status** thread is now a **Tuple(ResultCode, Message)**
* **SetDelay** command is renamed to **SetDelayInfo** for HelperSubarrayDevice and HelperDishDevice
* SetException is removed from Helper Devices
* **Decorators** are updated to support the new **update_task_status** calls.
* **HelperCspSubarrayDevice** is removed.
* **COMMAND_NOT_ALLOWED** fault type is changed to **COMMAND_NOT_ALLOWED_BEFORE_QUEUING**
* New fault types **COMMAND_NOT_ALLOWED_AFTER_QUEUING** and **COMMAND_NOT_ALLOWED_EXCEPTION_AFTER_QUEUING** introduced
* **max_workers** parameter removed from component manager

[0.16.8]
*********
* Update in the way the helper dish device sends the resultcode and message
* Use push_command_result instead of push_command_status

[0.16.7]
***********
* Fix the dish unavailability issue observed in tmc-mid integration repository
* Update achieved pointing events push logic in helper dish device

[0.16.6]
***********
* Fix issues in **timeout_decorator** and **Error error_propagation_decorator**

[0.16.5]
***********
* Revert the changes done in 0.16.2.

[0.16.3]
***********
* Fix dish leaf node helper device configure command dish mode event push issue.

[0.16.1]
************
* HelperSubarray Devices no longer pushes events if the command invoked is **Abort**.

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