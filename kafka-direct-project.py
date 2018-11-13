
"""
 Processes direct stream from kafka, '\n' delimited text directly received
   every 2 seconds.
 Usage: kafka-direct-iotmsg.py <broker_list> <topic>

 To run this on your local machine, you need to setup Kafka and create a
   producer first, see:
 http://kafka.apache.org/documentation.html#quickstart

 and then run the example
    `$ bin/spark-submit --jars \
      external/kafka-assembly/target/scala-*/spark-streaming-kafka-assembly-*.jar \
      kafka-direct-iotmsg.py \
      localhost:9092 iotmsgs`
"""
from __future__ import print_function

import sys
import re

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import SQLContext
import folium


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: kafka-direct-iotmsg.py <broker_list> <topic>", file=sys.stderr)
        exit(-1)

    sc = SparkContext(appName="LandMinesSensorAnalysis")
    ssc = StreamingContext(sc, 10)

    sc.setLogLevel("WARN")
    spark = SQLContext(sc)

    ###############
    # Globals
    ###############
    #tempTotal = 0.0
    ObservationCount = 0
    HighAlarmCount = 0
    ModerateAlarmCount = 0
    LowAlarmCount = 0
    FalseAlarmCount = 0
    
    #tempAvg = 0.0

    brokers, topic = sys.argv[1:]
    kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})

    # Read in the Kafka Direct Stream into a TransformedDStream
    lines = kvs.map(lambda x: x[1])
    #lines.pprint(1)
    ############
    # Processing
    ############
    # foreach function to iterate over each RDD of a DStream
    def processLandMinesRDD(time, rdd):
      print("========= %s =========" % str(time))
      # Match local function variables to global variables
      global ObservationCount
      global HighAlarmCount
      global ModerateAlarmCount
      global LowAlarmCount
      global FalseAlarmCount
      try:
       jsonString = rdd.map(lambda x:re.sub(r"\s+", "", x, flags=re.UNICODE)).reduce(lambda x,y:x+y)
       #print("jsonString = %s" % str(jsonString))
       # Convert the JSON string to an RDD
       jsonRDDString = sc.parallelize([str(jsonString)])
       print("parallelize done\n=====")
       

       # Convert the JSON RDD to Spark SQL Context
       jsonRDD = spark.read.json(jsonRDDString)
       print("spark.read.json\n=====")

       print("List of mines\n=====")
       jsonRDD.printSchema()
       jsonRDD.registerTempTable("MinedSensorTable")
       
       print(".........................Environmental Factors.................................\n")
       spark.sql("select EMI_frequency,\
           GPR_bandwidth,\
            cover,\
             soil.moisture Soil_Moisture,\
             soil.type Soil_type,\
             weather,\
             destination,\
              eventTime\
              from MinedSensorTable").show()
       

       print("..............List of False Alarm objects....................\n")
       fldf=spark.sql("select payload.data.latitude, payload.data.longitude,\
             payload.data.height, payload.data.length,\
             case when payload.data.Metal=0 then 'Plastic'\
                  when payload.data.Metal=1 then 'Partial Metal'\
                  when payload.data.Metal=2 then 'Metal' \
                  end as Type_of_Material,\
             case when payload.data.depth<=3 then 'Surfaced'\
                  when payload.data.depth>3 then 'Buried'\
                  end as Depth,\
            case when payload.data.size=1 then 'Small'\
                  when payload.data.size=2 then 'Large'\
                  end as Size\
             from MinedSensorTable\
             where payload.data.confidence<=2")
       fldf.show()
      
       print("..............List of Land Mines....................\n")
       lmdf=spark.sql("select payload.data.latitude, payload.data.longitude,\
             payload.data.height, payload.data.length,\
             case when payload.data.Metal=0 then 'Plastic'\
                  when payload.data.Metal=1 then 'Partial Metal'\
                  when payload.data.Metal=2 then 'Metal' \
                  end as Type_of_Material,\
             case when payload.data.depth<=3 then 'Surfaced'\
                  when payload.data.depth>3 then 'Buried'\
                  end as Depth,\
            case when payload.data.size=1 then 'Small'\
                  when payload.data.size=2 then 'Large'\
                  end as Size,\
            payload.data.confidence,\
            payload.data.nitrogenLevel,\
            case when payload.data.confidence=6 and payload.data.nitrogenLevel='high' then 'High Alarm'\
                 when payload.data.confidence<6 and payload.data.nitrogenLevel='high' then 'Moderate Alarm'\
                 when payload.data.confidence<6 and payload.data.nitrogenLevel='low' then 'Low Alarm'\
                 else 'Insufficient Data' end as Alarm_Status\
            from MinedSensorTable\
            where payload.data.confidence>2\
            order by payload.data.nitrogenLevel desc")
       lmdf.show()

       HighAlarmCount+=lmdf.filter("Alarm_Status=='High Alarm'").count()
       ModerateAlarmCount+= lmdf.filter("Alarm_Status=='Moderate Alarm'").count()
       LowAlarmCount+=       lmdf.filter("Alarm_Status=='Low Alarm'").count()
       FalseAlarmCount+=fldf.count()
       ObservationCount+=jsonRDD.count()
        
       print("Total messages"+str(ObservationCount))
       print("No. of High Priority Land Mines:"+' '+str(HighAlarmCount))
       print("No. of Moderate Priority Land Mines:"+' '+str(ModerateAlarmCount))
       print("No. of Low Priority Land Mines:"+' '+str(LowAlarmCount))
       print("No. of False Alarms:"+' '+str(FalseAlarmCount))
       
       print("..............Generating Map....................\n")

       loc=lmdf.toPandas()
       map_hooray = folium.Map(zoom_start = 10)
       for i in range(0,len(loc)):
          folium.Marker([loc['latitude'][i],loc['longitude'][i]],popup=loc['Alarm_Status'][i],).add_to(map_hooray)
       map_hooray.save("/home/ec2-user/Project/MinesLocation.html")

       spark.dropTempTable("MinedSensorTable")
       jsonRDDString.unpersist()
       jsonRDD.unpersist()
      except Exception as e: 
         print(e)

    lines.foreachRDD(processLandMinesRDD)
    spark.clearCache()
    ssc.start()
    ssc.awaitTermination()
