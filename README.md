# SmartThings-InfluxDB-logger
Python script to poll SmartThings devices and write data to InfluxDB.

### Background
Samsung Smartthings platform upgrade obsoleted Groovy smartapps inclusing [InfluxDB Logger v1.11](https://github.com/codersaur/SmartThings) that was easy to use, highly configurable, and effective at logging SmartThings device data to InfluxDB enabling dashboard creation.  Search results have not identified an equivalent replacement.  And any event-driven design, like in the original Groovy InfluxDB Logger smartapp requires complex web server design involving Amazon LambdaAWS or Node.js which is beyond my skills and appetite for complexity.

In an effort to achieve a simple solution, I developed Python script [InfluxDBlogger.py](../main/InfluxDBlogger.py).  This script has been working well for me on my Raspberry PI 3B and can run on many platforms.  Since it is not event-driven, it does not provide real-time up data updates like the Groovy InfluxDB Logger smartapp.  Instead it polls devices similar to the soft-polling in the smartapp.

An added feature is that data is only written if the device is online.  Once a device goes offline, data logging stops and is easily detected on a dashboard chart.  In addition, device online/offline status is written to InfluxDB enabling creation of [device status dashboards](https://github.com/AllegrettoA/SmartThings-InfluxDB-logger/blob/main/Example%20Device%20Status%20Dashboard.png) like the example in this repository.

<p align="center"><img src="https://github.com/AllegrettoA/SmartThings-InfluxDB-logger/blob/main/Example%20Device%20Status%20Dashboard.png" width="400"></p>

Note that the script only writes data for capabilities power, battery, and temperature since those are the only ones that matterd to me.  However, you can copy and paste code to write data for other capabilities.  I recommend adding a line of code print(dev) to examine the json structure for other device capabilities and it will be arrarent how to write its data.

### Setup
Personal Access Token.  Since the script runs external to SmartThings, a Personal Access Token is required.  This access token enables the Python app (or any other app) to have access to your SmartThings devices and eliminates the need for login credentials.  You can generate a Personal Access Token by logging on to your SmartTHings account and navigating to https://account.smartthings.com/tokens.  Add your access token to the AccessToken variable.

InfluxDB Connection.  Configure the InfluxDB connection variables with your username, password, database name, host name or IP address, and port number.

Run Script.  Either use command tool to run Python script or add to your startup file.  For Raspberry PI, you can modify rc.local file with command '*sudo nano /etc/rc.local*', then add this code to the bottom:

    # Run SmartThings InfluxDatalogger Python script
    sleep 30 && python3 /home/pi/shared/SmartThings/InfluxDBlogger.py &
