# CIWS-WM-Node

This repository contains hardware and software designs for a computationally-enabled water meter datalogger. The hardware is made up of two parts. One part is a Raspberry Pi embedded computer that serves as the computational resource. The Raspberry Pi is coupled with a data acquisition device that is based on an Arduino Pro and is similar to our simplified datalogger for magnetically-driven residential water meters (See UCHIC/CIWS-MWM-Logger).

The data acquisition device is primarily responsible for processing magnetometer data and storing flow data from the water meter. Secondarily, it controls power to the Raspberry Pi in order to conserve battery life and reduce overall power consumption/requirements. Once powered, the Raspberry Pi retreives the flow data and processes it to compute useful summaries of water use and identify water end-uses.

The 'Firmware' directory contains the firmware for the data acquisition device, or AVR Datalogger.

The 'Software' directory contains the software for the Raspberry Pi.

The 'Hardware' directory contains hardware design information.

The 'Docs' directory contains documentation

This device is still under development.

## Cyberinfrastructure for Intelligent Water Supply (CIWS) 

CIWS is a project funded by the U.S. National Science Foundation to develop cyberinfrastructure for smart water metering and high resolution water-use data collection. We are developing systems for high resolution residential water consumption data collection, processing and analysis.

## Sponsors and Credits
[![NSF-1552444](https://img.shields.io/badge/NSF-1552444-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1552444)

This work was supported by National Science Foundation Grant [CBET 1552444](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1552444). Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the National Science Foundation.

