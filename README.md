# Spark-and-Kafka_IoT-Data-Processing-and-Analytics
IoT Project for UCSC Internet of Things
Developed a Spark Streaming Application which consumes data from Kafka and data analysis using Spark SQL.

Simulated data for this project using Python Simulator which generates JSON messages. 

{
  "guid": "0-ZZZ123456781D",
  "destination": "0-AAA12345678",
  "GPR_bandwidth" : "500 MHz",
  "EMI_frequency" : "75 Hz",
  "weather" : "overcast",
  "soil" : {
     "type" : "silt",
     "moisture" : "dry"
      } ,
  "cover" : "rocks",
  "eventTime": "2018-11-05T06:42:38.001051Z",
  "payload": {
     "format": "urn:land-mine-detector:sensor:lat-long-depth-length-size-metal",
     "data": {
       "latitude": 14.78,
       "longitude": 107.35,
       "depth": 0.43,
       "length": 1.00,
       "height": 11.00,
       "nitrogenLevel" : "high",
       "metal" : 2,
       "size" : 1,
       "confidence" : 1
     }
   }
}

Used Pyspark, HiveContext to analyze the data and presented it in Python folium map.

