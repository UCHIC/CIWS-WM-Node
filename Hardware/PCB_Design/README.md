# Manufacturing
This folder contains all the files necessary for manufacturing a printed circuit board (PCB) version of the CIWS-WM-Node. The PCB contains everything needed to interface with a Raspberry Pi computer and magnetometer sensor to collect and process data.

The `.pro` and `.sch` files are the board layout and schematic respectively. Use these two files with the `.kicad_pcb` file to view the design in kicad.

The `.csv` file and `.zip` files are used for manufaturing the devices. The `.zip` file contains the drill file, gerber files, assembly drawings, and position files. The `.csv` is a list of components used on the device. 

# Instructions for setting up the PCB After Manufacture

1. Remove the jumper on the `EEPROM Power` pins.
2. Connect the micro usb port on the PCB to your computer using a USB cable and turn the `PWR` switch on the PCB ON.
3. Connect your computer to the 6 header pins on the PCB with an AVR in-system programmer (ISP). Make sure to plug in the ribbon cable the right direction. A suitable AVR ISP is referenced in the link below.
4. Open up the code in the `Firmware` directory from this repository using the Arduino IDE and click on `Tools`. Select `Arduino Pro or Pro mini` as the board, `Atmega328P (3.3V 8MHZ)` as the processor, and `AVR ISP` as the programmer.
5. While still in the Arduino IDE, click `Burn Bootloader`. Wait for it to finish.
6. Unplug the AVR ISP from the PCB and turn the `PGRM` switch on the PCB ON.
7. In the `Tools` menu of the Arduino IDE, select the serial port connected to the micro usb port. If you are unsure which one is correct you can unplug the USB cable and see which one disappears. Reconnect the USB cable and select that one.
8. In the Arduino IDE, click `Upload`. This unploads the code onto the ATMEGA328P chip.
9. Turn the `PWR` and `PRGM` switches off on the PCB. 
10. Put the jumper back on the `EEPROM Power` pins on the PCB. 

Once these steps are complete, the PCB is ready to be snapped onto the header of a Raspberry Pi for use.

A suitable AVR ISP: https://www.pololu.com/product/3172
