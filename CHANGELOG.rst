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

[0.14.1]
************
* The scan_id as an argument related changes have been made for scan command in HelperDishDevice and HelperDishLNDevice
* EndScan command has been introduced in in HelperDishDevice and HelperDishLNDevice
* **scanID** attribute has been introduced in HelperDishDevice


Fixed
-----

* Fixed Pylint warnigs
* Fixed docstrings warnings
