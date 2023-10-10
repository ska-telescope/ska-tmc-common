

TMC Common Tango Helper Devices
================================


TMC uses helper devices instead of real devices to test component level functionality and also functionality of overall integrated TMC in TMC integration repository.
These Devices are used by multiple TMC repositories so kept in common repository to have functionality readily available across TMC repositories.

Devices and their functionality
-------------------------------

This page contains all the helper devices used by TMC to mock behavior of sub-systems,leaf nodes or subarray device.
Each helper device exposes required API's similar to real device.


Functionality
-------------
Few Functionality provided by the helper devices are as follows:

- SetDirectObsState: used to set device obsState directly.

- SetDirectState: Used to set device state directly.

- commandCallInfo: Used to get information of arguments used to call the command

- SetDelay: Used to produce delay in execution of commands to mimic real scenario.

- resetDelay: Used to reset delay to default one.

- Fault Injection: To make devices faulty to check error handling in tango devices.

- AddTransitions: This command will set duration for obs state such that whenrespective command for obs state is triggered then it change obs state
after provided duration.


Device List
===========

1. Helper_CSP_Master
--------------------
.. automodule:: ska_tmc_common.test_helpers.helper_csp_master_device
.. autoclass:: ska_tmc_common.test_helpers.helper_csp_master_device.HelperCspMasterDevice
   :members:
   :undoc-members:
   :show-inheritance:


2. Helper_CSP_Subarray
----------------------
.. automodule:: ska_tmc_common.test_helpers.helper_csp_subarray_leaf_device
.. autoclass:: ska_tmc_common.test_helpers.helper_csp_subarray_leaf_device.HelperCspSubarrayLeafDevice
   :members:
   :undoc-members:
   :show-inheritance:

3. Helper_Dish_Device
---------------------
.. automodule:: ska_tmc_common.test_helpers.helper_dish_device
.. autoclass:: ska_tmc_common.test_helpers.helper_dish_device.HelperDishDevice
   :members:
   :undoc-members:
   :show-inheritance:

4. Helper_SDP_Subarray
----------------------
.. automodule:: ska_tmc_common.test_helpers.helper_sdp_subarray
.. autoclass:: ska_tmc_common.test_helpers.helper_sdp_subarray.HelperSdpSubarray
   :members:
   :undoc-members:
   :show-inheritance:

5. Helper_SDP_Subarray_leaf_Device
----------------------------------
.. automodule:: ska_tmc_common.test_helpers.helper_sdp_subarray_leaf_device
.. autoclass:: ska_tmc_common.test_helpers.helper_sdp_subarray_leaf_device.HelperSdpSubarrayLeafDevice
   :members:
   :undoc-members:
   :show-inheritance:

6. Helper_StateMCCS_Device
--------------------------
.. automodule:: ska_tmc_common.test_helpers.helper_state_mccsdevice
.. autoclass:: ska_tmc_common.test_helpers.helper_state_mccsdevice.HelperMCCSStateDevice
   :members:
   :undoc-members:
   :show-inheritance:

7. Helper_Subarray_Device
-------------------------
.. automodule:: ska_tmc_common.test_helpers.helper_subarray_device
.. autoclass:: ska_tmc_common.test_helpers.helper_subarray_device.HelperSubArrayDevice
   :members:
   :undoc-members:
   :show-inheritance:


8. Helper_Subarray_Leaf_Device
------------------------------
.. automodule:: ska_tmc_common.test_helpers.helper_subarray_leaf_device
.. autoclass:: ska_tmc_common.test_helpers.helper_subarray_leaf_device.HelperSubarrayLeafDevice
   :members:
   :undoc-members:
   :show-inheritance:

9. Helper_Dish_LN_Device
---------------------
.. automodule:: ska_tmc_common.test_helpers.helper_dish_ln_device
.. autoclass:: ska_tmc_common.test_helpers.helper_dish_ln_device.HelperDishLNDevice
   :members:
   :undoc-members:
   :show-inheritance:


Conclusion
-----------

This module contain all helper devices required in TMC for testing and debugging




.. .. toctree::
..    :maxdepth: 2

.. .. automodule:: ska_tmc_common.tango_server_helper
.. .. autoclass:: ska_tmc_common.tango_helper_devices.TangoHelperDevices
..    :members:
..    :undoc-members: