#SmartThings Influx data logger.
#Replaces original Groovy event-based InfluxDB-logger Smartapp.
#Requires SmartThings Personal Access Token
#Writes data only if device health state in ONLINE
#Author:    Allen Allegretto
#Version:   1.0 (2023-01-27)
#Revisions:
#           1.1 (2020-01-29) Added device health, added polling data

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
        print (myLabel, ': ', myMeasurement, '  ', myValue, myUnit, '  ', myDatetime,)
        
    except:
        pass
    


#Main procedure to quesry each device and log data
def UpdateSmartThingsData():
    
    #connect to influx
    global ifclient
    ifclient = InfluxDBClient(ifhost,ifport,ifuser,ifpass,ifdb)

    # URL and Authourzation token from SmartThings
    url = 'https://api.smartthings.com/v1/devices'
    headers = {
        'Authorization': 'Bearer ' + AccessToken,
        'cache-control': 'no-cache'
        }

    # Get Devices and search each device for select capabilities
    jsonDevices = requests.get(url, headers=headers).json()
    for dev in jsonDevices['items']:
        #convert dict of capabilities to string for to easy check if contains specific capability
        strCapabilities = str( dev['components'][0]['capabilities'])
        
        #Log specific capabilities
        if ('powerMeter' in strCapabilities) \
        or ('battery' in strCapabilities) \
        or ('temperatureMeasurement' in strCapabilities):
            time = datetime.datetime.utcnow()    #2023-01-24 18:41:44.584187
            
            #query device health to check if ONLINE of OFFLINE
            deviceId = dev['deviceId']
            jsonHealth = requests.get(url + '/' + deviceId + '/health', headers=headers).json()
            LogInfluxData('SmartthingsHealth', time, 'status', deviceId, dev['label'], dev['locationId'], jsonHealth['state'])
            
            #write influx data if device ONLINE
            if (jsonHealth['state'] == 'ONLINE'):
                
                #query device status data
                jsondata = requests.get(url + '/' + deviceId + '/status', headers=headers).json()

                #log capability data
                if ('powerMeter' in strCapabilities):
                    myValue = jsondata['components']['main']['powerMeter']['power']['value']
                    myUnit = jsondata['components']['main']['powerMeter']['power']['unit']
                    LogInfluxData('power', time, myUnit, deviceId, dev['label'], dev['locationId'], myValue)

                if ('battery' in strCapabilities):
                    myValue = jsondata['components']['main']['battery']['battery']['value']
                    myUnit = jsondata['components']['main']['battery']['battery']['unit']
                    LogInfluxData('battery', time, myUnit, deviceId, dev['label'], dev['locationId'], myValue)

                if ('temperatureMeasurement' in strCapabilities):
                    myValue = jsondata['components']['main']['temperatureMeasurement']['temperature']['value']
                    myUnit = jsondata['components']['main']['temperatureMeasurement']['temperature']['unit']
                    LogInfluxData('temperature', time, myUnit, deviceId, dev['label'], dev['locationId'], myValue)
                    
            else:
                pass

    #close influx
    ifclient.close()

    print ('Completed ', datetime.datetime.utcnow(), '  Process time: ', ts2 - ts1)
    print ('Waiting...')


#Update data every 5 minutes
while True:
    try:
        UpdateSmartThingsData()
    except:
        pass
    sleep(60 * PollIntervalMinutes)


quit()
