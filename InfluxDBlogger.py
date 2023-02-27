#SmartThings Influx data logger.
#Replaces original Groovy event-based InfluxDB-logger Smartapp.
#Requires SmartThings Personal Access Token
#Writes data only if device health state in ONLINE
#Author:    Allen Allegretto
#Version:   1.0 (2023-01-27) Original
#           1.1 (2023-01-29) Added device health and polling stats data
#           1.2 (2023-02-15) Added logging for debugging
#           1.3 (2023-02-26) Batch mode using REST API version 20170916
#                            - Used by SDK, capable of batch query
#                            - Ref: https://community.smartthings.com/t/api-check-all-devices-health-in-batch/251420/5
#                            Added request timeout
#                            Removed logging


#Configuration:
#1. Provide SmartThings Personal Access Token
#2. InfluxDB credentials and database name
#3. Specify desired PollIntervalMinutes
#4. Add code for desired capabilities if needed.


import requests             # used for http requests
import datetime             # used to get current datetime
from time import sleep      # used for loop timer


#SmartThings Personal Access Token (https://account.smartthings.com/tokens
AccessToken = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'

# InfluxDB
from influxdb import InfluxDBClient
ifuser = "username"
ifpass = "password"
ifdb   = "home"
ifhost = "192.168.1.85"
ifport = 8086


#Interval to query SmartThings for device data
PollIntervalMinutes = 5



#Logs data point to InfluxDB
def LogInfluxData(myMeasurement, myDatetime, myUnit, myDeviceId, myLabel, myLocationId, myValue):
    try:
        # DB format the data as a single measurement for influx
        body = [
            {
                "measurement": myMeasurement,
                "time": myDatetime,
                "tags": {
                    "unit":  myUnit,
                    "deviceId": myDeviceId,
                    "deviceName": myLabel,
                    "locationId": myLocationId
                },
                "fields": {
                    "value": myValue
                }
            }
        ]
        #write data
        ifclient.write_points(body)
        #print (myLabel, ': ', myMeasurement, '  ', myValue, myUnit, '  ', myDatetime,)
        
    except:
        pass
    

#Logs poll data point to InfluxDB
def LogInfluxPollData(myMeasurement, myDatetime, myUnit, myLabel, myValueRequest, myValueProcess, onlineCount, offlineCount, offlineDevices):
    try:
        # DB format the data as a single measurement for influx
        body = [
            {
                "measurement": myMeasurement,
                "time": myDatetime,
                "tags": {
                    "unit":  myUnit,
                    "deviceName": myLabel
                },
                "fields": {
                    "requestSeconds": myValueRequest,
                    "processSeconds": myValueProcess,
                    "onlineCount": onlineCount,
                    "offlineCount": offlineCount,
                    "offlineDevices": offlineDevices
                }
            }
        ]
        #write data
        ifclient.write_points(body)
        #print (myLabel, ': ', myMeasurement, '  ', myValueRequest, myValueProcess, myUnit, '  ', onlineCount, offlineCount, offlineDevices)
        
    except:
        pass




#Main procedure to quesry each device and log data
def UpdateSmartThingsData():
    # ts stores the time in seconds
    ts1 = datetime.datetime.utcnow()
    listOffline = []
    onlineCount = 0
    offlineCount = 0
    
    #connect to influx
    global ifclient
    ifclient = InfluxDBClient(ifhost,ifport,ifuser,ifpass,ifdb)

    # URL and Authourzation token from SmartThings
    url = 'https://api.smartthings.com/devices?includeStatus=true&includeHealth=true'
    headers = {
        'Authorization': 'Bearer ' + AccessToken,
        'Accept': 'application/vnd.smartthings+json;v=20170916',
        'cache-control': 'no-cache'
        }

    # Get Devices and search each device for select capabilities
    jsonDevices = requests.get(url, headers=headers, timeout=10).json()
    ts2 = datetime.datetime.utcnow()
    
    # Process each device with desired capabilities
    for dev in jsonDevices['items']:
        #convert dict of capabilities to string for to easy check if contains specific capability
        strCapabilities = str( dev['components'][0]['capabilities'] )
        
        #Log specific capabilities
        if ('powerMeter' in strCapabilities) \
        or ('battery' in strCapabilities) \
        or ('temperatureMeasurement' in strCapabilities):
            
            #Log status ONLINE of OFFLINE
            time = datetime.datetime.utcnow()
            LogInfluxData('SmartthingsHealth', time, 'status', dev['deviceId'], dev['label'], dev['locationId'], dev['healthState']['state'])
        
            #write influx data if device ONLINE
            if (dev['healthState']['state'] == 'ONLINE'):
                onlineCount += 1

                #log each capability
                for cap in dev['components'][0]['capabilities']:
                    if (cap['id'] == 'powerMeter'):
                        myValue = cap['status']['power']['value']
                        myUnit = cap['status']['power']['unit']
                        LogInfluxData('power', time, myUnit, dev['deviceId'], dev['label'], dev['locationId'], myValue)
                        
                    if (cap['id'] == 'battery'):
                        myValue = cap['status']['battery']['value']
                        myUnit = cap['status']['battery']['unit']
                        LogInfluxData('battery', time, myUnit, dev['deviceId'], dev['label'], dev['locationId'], myValue)
                        
                    if (cap['id'] == 'temperatureMeasurement'):
                        myValue = cap['status']['temperature']['value']
                        myUnit = cap['status']['temperature']['unit']
                        LogInfluxData('temperature', time, myUnit, dev['deviceId'], dev['label'], dev['locationId'], myValue)

            else:
                offlineCount += 1
                listOffline.append(dev['label'])



    # ts stores the time in seconds
    ts3 = datetime.datetime.utcnow()

    #Log poll stats
    LogInfluxPollData('SmartthingsPoll', ts3, 'seconds', 'PythonScript', (ts2 - ts1).total_seconds(), (ts3 - ts2).total_seconds(), onlineCount, offlineCount, ', '.join(i for i in listOffline))
    
    #close influx
    ifclient.close()



#Update data every 5 minutes
while True:
    try:
        UpdateSmartThingsData()
    except:
        #print(sys.exc_info()[1])
        pass
    sleep(60 * PollIntervalMinutes)


quit()
