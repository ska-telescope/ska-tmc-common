###########
Change Log
###########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

Added
-----


[0.14.0]
************

* Update pytango v9.4.2
* Variable **SetisSubsystemAvailable** is change to **SetSubsystemAvailable**
* .darglint file to accomadate sphinx style rst documentation
* TimeKeeper class added for handling timout functionality
* Input type for **start_tracker_thread** method for param **state_function** is changed from **Callable** to **str**
* **timeout_decorator** and **error_propagation_decorator** added for implementing timeout and error propagation functionalities respectively

[0.15.0]
************
* Updated Scan command interface to include scan_id as argument
* EndScan command has been added in HelperDishLNDevice
* **scanID** attribute has been introduced in HelperDishDevice


Fixed
-----

[0.15.1]
************

* Updated **push_command_result** method from the HelperBaseDevice to take correct number of arguments
* The sequence of executing cleanup and **update_task_status** method is reversed in the Tracker Thread

[0.14.0]
************

* Fixed Pylint warnigs
* Fixed docstrings warnings
