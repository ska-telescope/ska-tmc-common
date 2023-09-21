
Introduction
============================================


This is a shared repository for common classes required for Telescope Monitoring and Control(TMC) work package of SKA Telescope software.

The ska-tmc-common repository contains implementation of Tango abstraction layer. It provides the abstraction in form of following classes:

**TangoClient**: Class that provides abstraction for Tango client APIs [deprecated]

**TangoGroupClient**: Class that provides abstraction for Tango group APIs [deprecated]

**TangoServerHelper**: Class that provides abstraction for Tango device server APIs [deprecated]

**TangoHelperDevices**: Class that provides abstraction for various TMC Tango devices for testing and debugging

**Adapters**: Module used to create adapter for all the devices.

**Liveliness Probe**: Module contains classes to manage liveliness probe on the devices. 

**TMC Command**: Module contains classes that have generic command class functionality and is inherited by all the other TMC Command Classes

**TangoHelperDevices**: Module contains classes that have generic component manager functionality and is inherited by all other Component Manager Classes.