# SmartThings-InfluxDB-logger
Python script to poll SmartThings devices and write data to InfluxDB.

## Background
Samsung Smartthings platform upgrade obsoleted Groovy smartapps inclusing one that was easy to use, highly configurable, and effective at logging SmartThings device data to InfluxDB (https://github.com/codersaur/SmartThings).  Search results have not identified equivalent replacements.  And any event-driven design, like in the original Groovy smartapp requires complex web server design beyond my capabilities.

In an effort to achieve a simple solution, I developed Python script InfluxDBlogger.py.  This script has been working well for me on my Raspberry PI 3B and can run on many other platforms.

Since the script runs external to SmartThings, a Personal Access Token is required.  This access token enables the Python app (or any other app) to have access to your SmartThings devices and eliminates the need for login credentials.  You can generate a Personal Access Token by logging on to your SmartTHings account and navigating to https://account.smartthings.com/tokens.
