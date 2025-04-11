###########
Change Log
###########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

Main
--------
* Improved Code coverage


Added
--------
[0.26.1]
********
* Added changes in the logs as per Logging Guidelines.
* Update livelinessprobe to remove redundant logging and implememted prettty printing for logs containing json data.

[0.26.0]
********
* Added new class EventManager to manage event subscriptions/umsubscriptions and event errors.
* Updated component manager and liveiness probe classes to co-ordinate with new event manager functionality.

[0.25.1]
********
* Handled signature inconsistencies in event update methods.
* Event Handler methods updated for queue based processing.

[0.25.1]
********
* Added Abort command in MCCS master leaf node adapter

[0.25.0]
********
* Updated ska-tango-base to v1.2.0

[0.24.9]
********
* Updated event receiver handlers to introduce queue based processing

[0.24.8]
********
* Updated SDP subarry helper device to induce error during Scan command

[0.24.7]
********
* Implemented the SetAdminMode command for helper leaf devices

[0.24.6]
********
* Updated helper dish device to push dish subsystems LRCR events (same as DishManager)

[0.24.0]
********
* Add common functionality of adminMode in ska-tmc-common

[0.23.0]
*********
* Adding Admin mode functinality in helper devices
[0.22.16]
*********
* Enable induce_fault functionality in HelperSDPSubarray

[0.22.15]
*********
* Update the helper dish master to send pointing state slew before track in track command.
  
[0.22.14]
*********
* clean up method of observable called before calling update task status

[0.22.13]
*********
* Update the helper mccs subarray device to push change the result after obsstate scanning

[0.22.12]
********
*  Fixed dish master Trackstop command to stop Track command.
*  Added dishMode property in dish adpaters.

[0.22.11]
*********
* SN will check for LRCR from all the subsystems and hence Updated subarry leaf node and dish leaf node  helpers to support Scan command completion by sending LRCRs

[0.22.10]
*********
* Updated HelperSubarrayDevice to push chant event for longrunningcommandresult attribute for Scan command.

[0.22.9]
********
* Fixed SKB-618(Fix KeyError for Missing 'resources' Key in SDP Subarray AssignResources Command)

[0.22.8]
********
* Updated SetPointingOffset to NextPointingOffset in DishlnPointingDeviceAdapter. 

[0.22.7]
********
* Updated ChangePointingOffsets to SetPointingOffset in DishlnPointingDeviceAdapter. 

[0.22.6]
********
* Updated received addresses value.

[0.22.5]
********
* Added DishLeaf Node pointing device adapter.
* Added properties and methods to the DishLeaf node pointing device adapter.

[0.22.2]
********
* Added change_event for band params in helper dish device.

[0.22.2]
********
* Added trackTableLoadMode attribute on the helper dish device.


[0.22.1]
* Updated helper dish devices to support Dish error proagation testing on TMC SubarrayNode 

[0.22.0]
* Updated Command ApplyPointingModel in HelperDishDevice and HelperDishLeafnode

[0.21.1]
* Resolved skb-536.
* SDP Subarray Device is able to go to ABORTING state before ABORTED.

[0.21.0]
* Update error propagation to event based.
* Removed usage of tracker thread.
* Added new classes Observer, Observable and CommandCallbackTracker.
  
[0.20.5]
* Update helper dish device to simulate the error propagation and timeout scenarios

[0.20.4]
* Update output_host and output_port values in receive addresses.

[0.20.3]
* Enable error propagation and timeout simulation for helper dish commands

[0.20.0]
**********
* Updated liveliness probe to utilize state command and consider exported flag for device availability.

[0.19.8]
**********
*  Update HelperDishDevice to support Dish error propgation

[0.19.7]
**********
*  Abort event cleared in tracker thread

[0.19.6]
**********
* Include induce fault mechanism in sdp helper device

[0.19.5]
**********
* Push lrcr command result for Helper Dish Device End Scan command

[0.19.0]
**********
* Added ApplyPointingModel command in helper dish device to handle global pointing json.

[0.18.0]
**********
* Utilise SKA Tel Model with OSO-TMC Configure schema v4.0 for ADR-99 changes

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
-------
[0.25.1]
* Delay provided to allocate command of MCCS Master Leaf Node

[0.24.10]
* Fixed SKB-732 

[0.24.6]
* AdminMode command implementation on Leafnodes for SN testing

[0.24.5]
* admin mode attribute added for csp, sdp and mccs subarray leaf node helper devices

[0.24.4]
* Fix command id's for Track and TrackLoadStaticOff commands on helper dish device.

[0.24.3]
* Exception check added which is received before registering the observer

[0.24.2]
* Fixed issue with observers list.
* Fixed issue with backward compatibility by adding files back to ska_tmc_common folder.

[0.24.1]
* Resolved bug SKB-658 on TMC Central Node and SubarrayNode

[0.23.2]
*********
* Updated SDP Subarray leaf node.
  
[0.23.1]
* Resolved bug SKB-658 on TMC Leaf Nodes

[0.20.2]
* Fixed bug related to full trl usage in liveliness probe.

[0.20.1]
* Fixed dish and dish leaf node helper devices to push change event for dishMode.STANDBY_FP when AbortCommands() command is invoked.

[0.19.4]
* Fixed the issue in HelperBaseDevice to return faultmessage instead of command_id for FaultType.FAILED_RESULT .

[0.19.3]
**********
* Added TMCBaseLeafDevice

[0.19.2]
**********
* Add method in TMC base device to push change and archive events

[0.19.1]
**********
* Updating commandCallInfo attribute in TrackLoadStaticOff command

[0.17.12]
* Fixed the issue in logManager

[0.17.11]
* Fixed the issue of mock devices getting created in HelperAdapterFactory

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