# HA-MQTT-EaglePower
Home Automation Docker MQTT Service for The Rainforest Automation Eagle200 smart power meter

Uses the Local API offered by the Eagle 200. 
* [Eagle Uploader API Docs](https://rainforestautomation.com/wp-content/uploads/2020/01/EAGLE-Uploader-Specification-v2.5.pdf) 
* [Eagle Developer Page](https://www.rainforestautomation.com/support/developer/)

Home assistant offers a native [integration](https://www.home-assistant.io/integrations/rainforest_eagle/) for Eagle devices and works via local polling.
This works fine and feel free to use it instead of this project.

This project instead uses the Eagle's local push feature to push the data to a web endpoint running on this service 
after which it is posted to MQTT. This results in faster updates.

The downside is its more work to setup. With the Eagle having access to the internet you have to provision your device for Local Push use via their API calls.
Unfortunately I have not made this easy to do with this project. Check out the [Eagle Uploader API Docs](https://rainforestautomation.com/wp-content/uploads/2020/01/EAGLE-Uploader-Specification-v2.5.pdf) and read the section 
on **"Uploader Configuration"**. There you will need to configure your cloud account to push data to a local server. After which 
your eagle device will be provisioned to do so. At which point you can revoke internet access on your Eagle device as all comunication
will be happening locally. Feel free to read configure_device.py for an attempt at doing so. Your mileage may vary. Good Luck!

# Info about the Eagle 200
This device is a OpenWRT SoC with a pair of Zigbee radios.

# Security Concerns
The Eagle 200 connects to rainforestautomation's API services via an OpenVPN tunnel where your device is remotely managed. This device could potentially 
be granting them access to your local area network. I recommend setting up some kind of local service and then 
removing internet access from the device via firewall rules or vlans.