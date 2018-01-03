**************************
FogLAMP SensorPhone Plugin
**************************

This is a south side plugin for the FogLAMP project. It provides connectivity with the
SensorPhone application on a iPhone.

Building
========

In order to use this plugin

	Install and run the FogLAMP main project
	Set FOGLAMP_ROOT as specified in the FogLamp Project
	Run make
	Restart FogLAMP

SensorPhone App
===============

The SensorPhone App is available in the Apple App Store, see https://itunes.apple.com/gb/app/sensorphone/id1092304193?mt=8

Configure the SensorPhone application to POST data to FogLAMP by selecting
the *IoT Service* option.
	Set the URL to point at your FogLAMP plugin, http://<foglamp-host>:8080/
	Set the Mode to sync
	Set the Message Type to foglamp
	Leave the Message set to the develop value

To test the application click on the POST button, if all is well a single reading
will be ingested by FogLAMP.

To get continual readings click on the clock icon and select an interval at which to
send readings and then click on the POST button.
