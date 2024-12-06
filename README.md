# ArduinoPneumaticBoard
This is the repo for the pneumatic Board 

This repo consists of designs, instructions, and code to build and use the soft robotics lab pneumatic board. 

## Table of Contents
- [Directory](#directory)
- [Contributions](#contributions)

# Directory
```
0.0.0 |- README.md            <-- you are here
1.0.0 |- 3DMODELING                                     #all models we made for the pneumatic board
2.0.0 |- Data_collection                                #scripts for capturing data and files where
      |                                                  we kept all our data for storage
2.1.0 |  |- Angle_Data                                  #Arm strap video angle readings
2.2.0 |  |- Data                                        #Arm strap video resistance sensor readings
2.3.0 |  |- Arduino_Data_To_csv.py                      #Grabbing resistance sensor readings and
      |  |                                               storing them to csv files for training
      |  |                                               neural networks
2.4.0 |  |- analyze_solenoid_angle.py                  #taking angle from strap arm when given
      |  |                                              video input and processing it into csv
2.5.0 |  |- combine_res_angle.py                       #taking our angle readings and resistance
      |  |                                              readings to have a combined output csv
2.6.0 |  |- video_reading.py                           #script to match our resistance readings
      |  |                                              to the video of arm
3.0.0 |- Documentation                                 #All documents to do everything in repo
3.1.0 |  |- images                                     #folder containing all images used in
      |  |                                              repository
4.0.0 |- PneumaticBoard                                #folder containing all of our sketches
      |                                                 for using our pneumatic board manual
      |                                                 control setup
4.1.0 |  |-airpumpcontrol2                             # our most recent best working script for
      |  |                                               controlling pneumatic board
5.0.0 |- Sensors                                       #script we used for taking readings from
      |                                                 arduino, uploaded to our arduino
6.0.0 |- Checkports.py                                 # simple script made to ensure our
      |                                                  connection to the COM arduino ports is       |                                                  functional
```

# Contributions
Christian Diaz Herrera

Kido Douglas

Simon Chidley

Reese Chahal

Miles Modeste

Kevin Angulo

Chi Phan
