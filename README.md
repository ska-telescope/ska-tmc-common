# ska-tmc-common

## About

This is a shared repository for common classes required for Telescope Monitoring and Control(TMC) work package of SKA Telescope software.

The ska-tmc-common repository contains implementation of Tango abstraction layer. It provides the abstraction in form of following classes:
TangoClient: Class that provides abstraction for Tango client APIs
TangoGroupClient: Class that provides abstraction for Tango group APIs
TangoServer: Class that provides abstraction for Tango device server APIs

## Installation

### Requirements

The basic requirements are:

- Python 3.5
- Pip

The requirements for installation of the lmc bas classes are:

- enum34
- argparse
- future

The requirements for testing are:

- coverage
- pytest
- pytest-cov
- pytest-xdist
- mock

### Installation steps

1. Clone the repository on local machine.
2. Navigate to the root directory of the repository from terminal
3. Run 'python3 -m pip install . --extra-index-url https://nexus.engageska-portugal.pt/repository/pypi/simple'

## Testing

## Usage

The TMC common classes are installed as a Python package in the system. The intended usage of the base classes is to import the class according to the requirement. The class needs to be imported in the module.

To use the TangoClient, the usage is as follows:

```python
from ska.tmc.common import TangoClient
.  
.  
.  
my_client = TangoClient("device-FQDN")
my_client.send_command("DeviceCommand", param)
```
To use the TangoServerHelper class, the usage is as follows:

```python
from ska.tmc.common import TangoServerHelper
.  
.  
.  
my_server = TangoServerHelper.get_instance()
my_server.device = device
my_server.get_state()
```