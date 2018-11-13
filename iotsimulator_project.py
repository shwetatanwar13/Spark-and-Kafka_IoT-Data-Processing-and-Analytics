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
formatStr = "urn:land-mine-detector:sensor:lat-long-depth-length-size-metal"
minLatitudeVal = 9.17
maxLatitudeVal = 22.82
minLongitudeVal = 103.02
maxLongitudeVal = 109.32
GPR_bandwidthVal = "500 MHz"
EMI_frequencyVal = "75 Hz"
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
  "minLatitude" : %.2f,
  "maxLatitude" : %.2f,
  "minLongitude" : %.2f,
  "maxLongitude" : %.2f,
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
       "latitude": %.2f,
       "longitude": %.2f,
       "depth": %.2f,
       "length": %.2f,
       "height": %.2f,
       "nitrogenLevel" : "%s",
       "metal" : %d,
       "size" : %d, 
       "confidence" : %d
     }
   }
}"""

##### Generate JSON output:

print "["

dataElementDelimiter = ","
for counter in range(0, numMsgs):

  randInt = random.randrange(0, 9)
  randLetter = random.choice(letters)
  print iotmsg_header % (guidStr+str(randInt)+randLetter, destinationStr,minLatitudeVal,maxLatitudeVal,minLongitudeVal,maxLongitudeVal,GPR_bandwidthVal, \
                         EMI_frequencyVal,random.choice(weatherArray),random.choice(soilTypeArray),random.choice(soilMoistureArray),random.choice(coverArray))

  today = datetime.datetime.today()
  datestr = today.isoformat()
  print iotmsg_eventTime % (datestr)

  print iotmsg_payload % (formatStr)

  # Generate a random floating point number
  randLat = random.uniform(9.17,22.82)
  randLong = random.uniform(103.02,109.32)
  randDepth = random.uniform(0.00, 6.00)
  randHeight = random.randrange(0, 20)
  randLength = random.randrange(0, 30)
  randnitrogenLevel = random.choice(['low','high'])
  randMetal = random.choice([0,1,2])
  randSize = random.choice([1,2])
  randConfidence = random.randrange(0, 6)

  if counter == numMsgs - 1:
    dataElementDelimiter = ""
  print iotmsg_data % (randLat,randLong,randDepth,randLength,randHeight,randnitrogenLevel,randMetal,randSize,randConfidence) + dataElementDelimiter

print "]"

