#!/usr/bin/python

import sys
import datetime
import random
import string

# Set number of simulated messages to generate
if len(sys.argv) > 1:
  numMsgs = int(sys.argv[1])
else:
  numMsgs = 1

# Fixed values
guidStr = "0-ZZZ12345678"
destinationStr = "0-AAA12345678"
formatStr = "urn:land-mine-detector:sensor:lat-long-depth-length-height-nitlev-metal-conf"
EMI_frequencyVal = "75"
weatherArray = ['clear','overcast','rain']
soilTypeArray = ['clay','sand','silt','loam']
soilMoistureArray = ['wet','dry']
coverArray = ['none','vegetative','rocks','water']


# Choice for random letter
letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

iotmsg_header = """\
{
  "guid": "%s",
  "destination": "%s",
  "GPR_bandwidth" : "%s",
  "EMI_frequency" : "%s",
  "weather" : "%s",
  "soil" : {
     "type" : "%s",
     "moisture" : "%s"
      } ,
  "cover" : "%s", """

iotmsg_eventTime = """\
  "eventTime": "%sZ", """

iotmsg_payload ="""\
  "payload": {
     "format": "%s", """

iotmsg_data ="""\
     "data": {
       "latitude": %.6f,
       "longitude": %.6f,
       "depth": %.2f,
       "length": %.2f,
       "height": %.2f,
       "nitrogenLevel" : "%s",
       "metal" : %d, 
       "confidence" : %d
     }
   }
}"""

##### Generate JSON output:

print "["


randSoilType=random.choice(soilTypeArray)
randSoilMoisture=random.choice(soilMoistureArray)
randCover=random.choice(coverArray)
randWeather=random.choice(weatherArray)
#Calculate GPR_bandwidth based on soil type and moisture
if randSoilType=='clay' and randSoilMoisture=='wet':
  GPR_bandwidthVal=500
elif randSoilType=='sand' and randSoilMoisture=='dry':
  GPR_bandwidthVal=2000
else:
  GPR_bandwidthVal=1000

dataElementDelimiter = ","
for counter in range(0, numMsgs):

  print iotmsg_header % (guidStr, destinationStr,GPR_bandwidthVal, \
                         EMI_frequencyVal,randWeather,randSoilType,randSoilMoisture,randCover)

  today = datetime.datetime.today()
  datestr = today.isoformat()
  print iotmsg_eventTime % (datestr)

  print iotmsg_payload % (formatStr)

  # Generate a random floating point number
  randLat = random.uniform(13.820000,13.842828)
  randLong = random.uniform(109.000000,109.136699)
  randDepth = random.uniform(0.00, 7.00)
  randHeight = random.randrange(0, 20)
  randLength = random.randrange(0, 30)
  randnitrogenLevel = random.choice(['low','high'])
  randMetal = random.choice([0,1,2])
  randConfidence = random.randrange(0, 7)

  if counter == numMsgs - 1:
    dataElementDelimiter = ""
  print iotmsg_data % (randLat,randLong,randDepth,randLength,randHeight,randnitrogenLevel,randMetal,randConfidence) + dataElementDelimiter

print "]"

