This is a tutorial on how to use the pneumatic board when testing using arm straps

THE ARDUINO BOARD
1. <img src="images\circuit.jpeg" alt="step 1" width="50%" height=auto>
To ensure that the solenoid works functionally, first we want to plug in the red and green wires connected to the solenoid into the board. 
<img src="images\circuitwire.jpeg" alt="step 1" width="50%" height=auto>
The green wire should be plugged in to the right side of the board, in between the snubber diode and the transistor. The red wire should be plugged in to the left side of the board, right next to the left side of the snubber diode. 

2. <img src="images\powersupply.jpeg" alt="step 2" width="50%" height=auto>
Ensure that the power supply is set to release 7.5V. 

3. <img src="images\power.jpeg" alt="step 3" width="50%" height=auto>
Plug the power into the Arduino Mega.

4. <img src="images\valve.jpeg" alt="step 4" width="50%" height=auto>

Once the Arduino is plugged in, turn the blue dial to increase or decrease the rate at which the air is being released to the balloon straps. This dial controls the rate at which the solenoid will open and close for airflow.

THE AIRPUMP

5. <img src="images\pumpon.jpeg" alt="step 5" width="50%" height = auto>

First, we want to ensure that the airpump is plugged into a power source. Once that is complete, there are two important parts to be aware of. The top circled part is to turn on the airpump. The bottom knozzle is to release the air into our board. To fill the pump with air, flip the top red switch on and let it fill. (I usually fill the pump up to 30kpa, for our current 4 tube model. However you may need more or less depending on your needs)

6. <img src="images\tubeplug.jpeg" alt="step 6" width="50%" height=auto>

Take the air tube divider. Ensure that every output which will not be used is plugged so that no air is lost. Then ensure that the ones that will be used are plugged in correctly.

6a. <img src="images\regulator.jpeg" alt="step 6" width="50%" height=auto> 

At the input of the airtube divider a pressure regulator has been installed to allow for finer adjustments to the pressure release. To increases airflow, rotate the valve clockwise. Rotating the valve counter-clockwise decreases airflow.
<br>***note: the valve has a push lock. The adjustment is locked when pushed in, and unlocked when out***

7. <img src="images\tubing.jpeg" alt="step 7" width="50%" height=auto>

Now ensure that the tubes are correctly connected to the pneumatic board as shown in the image above. 

8. <img src="images\tubeplugin.jpeg" alt="step 8" width="50%" height=auto>

Plug our tube piece to the knozzle of the airpump. Once this is plugged in, air will immediately begin to flow out of the pump. Once air flows out, you can use the regulator to control the airflow into the balloons. Additionally, if you want more continuous airflow, you can turn on the airpump again to fill it while its releasing air.
<br> <b> Warning: The regulator acts as a bit of a buffer to ensuring steady outflow, though the airtank pressure will still build up at a faster rate than it is released.</b>

9. <img src="images\unplug.jpeg" alt="step 9" width="50%" height=auto>

Once finished, to unplug the tubing, pull on the knozzle as shown in the image. This will expel the tubing from the knozzle and stop the air flow. Additionally, if fully finished using the airpump, release the air from the bottom of the airpump using the small switch at the very bottom.


These are all the step to make the airpump/pneumatic board work. Update this document as we update our board.

Update Log:
- 11/4/2024 -- Miles Modeste
- 4/30/2024 -- Christian Diaz Herrera