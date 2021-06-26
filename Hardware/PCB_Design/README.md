# Manufacturing
This folder contains all the files necessary for manufacturing PCBs.

The `.pro` and `.sch` files are the board layout and schematic respectively. Use these two files with the `.kicad_pcb` file to view the design in kicad.

The `.csv` file and `.zip` files are used for manufaturing the devices. The `.zip` file contains the drill file, gerber files, assembly drawings, and position files. The `.csv` is a list of components used on the device. 

# Instructions for setting up the PCB
1. Remove the jumper on the `EEPROM Power` pins.
2. Connect the micro usb port to your computer and turn the `PWR` switch ON.
3. Connect your computer to the 6 header pins with an AVR ISP(make sure to plug in the ribbon cable the right direction). (A suitable AVR ISP is referenced in the link below)
4. Open up the code in the `Firmware` directory using the Arduino IDE and click on `Tools`. Select `Arduino Pro or Pro mini` as the board, `Atmega328P (3.3V 8MHZ)` as the processor, and `AVR ISP` as the programmer.
5. Click `Burn Bootloader`. Wait for it to finish.
6. Unplug the AVR ISP and turn the `PGRM` switch ON.
7. In `Tools` select the serial port connected to the micro usb port. If you are unsure which one is correct you can unplug it and see which one disappears. Reconnect it and select that one.
8. Click `Upload`. This unploads the code onto the ATMEGA328P chip.
9. Turn the `PWR` and `PRGM` switches off. Put the jumper back on the `EEPROM Power` pins. The PCB is ready for use.

AVR ISP: https://www.pololu.com/product/3172
