**************************
Fledge SensorPhone Plugin
**************************

This is a south side plugin for the Fledge project. It provides connectivity with the
SensorPhone application on a iPhone.

Building
========

In order to use this plugin

	Install and run the Fledge main project
	Set FLEDGE_ROOT as specified in the Fledge Project
	Run make
	Restart Fledge

SensorPhone App
===============

The SensorPhone App is available in the Apple App Store, see https://itunes.apple.com/gb/app/sensorphone/id1092304193?mt=8

Configure the SensorPhone application to POST data to Fledge by selecting
the *IoT Service* option.
	Set the URL to point at your Fledge plugin, http://<fledge-host>:8080/
	Set the Mode to sync
	Set the Message Type to fledge
	Leave the Message set to the develop value

To test the application click on the POST button, if all is well a single reading
will be ingested by Fledge.

To get continual readings click on the clock icon and select an interval at which to
send readings and then click on the POST button.
