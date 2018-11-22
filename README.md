

IoT: Real-time Data Processing and Analytics using Apache Spark / Kafka

Project Name: Land Mine Detector using IoT
	
Author: 		Shweta Tanwar
Created on: 		11/05/2018
Last updated on: 		11/19/2018
Version: 		1.0









	





Table of Contents
1.	Background	3
2.	Technologies Used	3
3.	Use Case	3
4.	Project Scenario	3
5.	Data Flow	4
6.	Format of sensor data	5
7.	Description of the Fields	6
8.	Command for sending data to Kafka	7
9.	Data Analysis	8














Background
During Vietnam War, countless number of land mines were planted on fertile land. Though the War ended in 1975, it is estimated that more than 3 million land mines are still buried there.
Since 1975, more than 40,000 people have died and more than 60,000 were injured due to this. These mines contain a deadly herbicide called Agent Orange which causes Cancer, Neurological damage and birth defects. 
Vietnam is not the only country where this issue exists, there are others. 
Though, there are many ongoing efforts to remove these Land mines, due to the sheer volume of these Mines, they are not enough.
This project tries to help in the solution of above problem using IoT.

Technologies Used

Apache Spark
Kafka
Python

Use Case
Analyze Data Provided by Mine Detector in Real Time.

Project Scenario 
Mine detector scans an area for land mines and sends data for analysis.
The detector sends data to a Kafka server in AWS Cloud (Simulated by feeding JSON data using Kafka-console-producer)
Kafka client retrieves the streaming data every 10 seconds
PySpark processes and analyzes them in real-time by using Spark Streaming, and show the results

Data Flow

Format of sensor data
The data for this project has been simulated using script iotsimulator_project.py. It generates JSON data as below format.
{
  "guid": "0-ZZZ12345678",
  "destination": "0-AAA12345678",
  "GPR_bandwidth" : "1000",
  "EMI_frequency" : "75",
  "weather" : "overcast",
  "soil" : {
     "type" : "silt",
     "moisture" : "wet"
      } ,
  "cover" : "rocks",
  "eventTime": "2018-11-19T06:04:16.547623Z",
  "payload": {
     "format": "urn:land-mine-detector:sensor:lat-long-depth-length-height-nitlev-metal-conf",
     "data": {
       "latitude": 13.829341,
       "longitude": 109.072547,
       "depth": 1.43,
       "length": 15.00,
       "height": 11.00,
       "nitrogenLevel" : "low",
       "metal" : 1,
       "confidence" : 3
     }
   }
}

Description of the Fields

Field	Description
 Guid	 A global unique identifier which is associated with the sensor. It has constant value as we are assuming that only one sensor is present.
destination	An identifier of the destination which sensors send data to (One single fixed ID is used in this project).
GPR_bandwidth	Ground Penetrating Radar bandwidth in MHz. This depends on the soil type and soil moisture. Value ranges from 500-2000MHz
EMI_frequency	Electromagnetic Induction Frequency in Hz. It is not affected by soil conditions so value is constant at 75Hz.
weather	 Current weather generated randomly from a list with values ['clear','overcast','rain']
soil.type	 Current soil type randomly from a list with values ['clay','sand','silt','loam']
soil.moisture	Current soil moisture randomly from a list with values
['wet','dry']
Cover	 Current soil top layer randomly from a list with values ['none','vegetative','rocks','water']
eventTime	 A timestamp that the data is generated.
payload.format	The format of data.
payload.data.latitude	Latitude of the probable mine object. For this project latitude values are randomly generated between (13.820000,13.842828)
payload.data.longitude	Longitude of the probable mine object. For this project latitude values are randomly generated between (109.000000,109.136699)
payload.data.depth	Depth below ground in cm of the probable mine object randomly generated between (0.00, 7.00)
payload.data.length	Length in cm of the probable mine object randomly generated between(0, 30)
payload.data.height	Height  in cm of the probable mine object  randomly generated between (0, 20)
payload.data.metal	 Randomly generated number between 0,2. 0=No metal, 1=Low metal and 2=High metal
payload.data.confidence	A higher confidence number implies a higher probability of a mine. This is internally calculated in the mine detector using several machine learning algorithms. For this project, it is randomly generated between 0-6. 6 meaning high probability of a mine and 0 meaning some man-made or natural clutter.


Command for sending data to Kafka

The messages are fed to Kafka broker by iotsimulator_project.py script using below command:

[ec2-user@ip-172-31-27-120 ~]$ python /home/ec2-user/Project/iotsimulator_project.py 5 | kafka_*/bin/kafka-console-producer.sh   --broker-list localhost:9092 --topic iotmsgs
Data Analysis
Each RDD of JSON messages in the Dstream is flattened into single line JSON message RDD. This RDD is then converted into Dataframe of RDD.
 
   jsonString = rdd.map(lambda x:re.sub(r"\s+", "", x, flags=re.UNI CODE)).reduce(lambda  
    x,y:x+y)
   # Convert the JSON string to an RDD
    jsonRDDString = sc.parallelize([str(jsonString)])       
   # Convert the JSON RDD to Spark SQL Context
    jsonRDD = spark.read.json(jsonRDDString)
 

The Dataframe is converted into a temporary table called MinedSensorTable.
       
    jsonRDD.registerTempTable("MinedSensorTable")

All the environmental settings are displayed which show current sensor settings and soil conditions. For a batch of messages same environmental settings will be displayed.


We display all the false alarms. False alarms are objects which have confidence less than 3. All the features like depth, material of the objects are displayed.

fldf=spark.sql("select payload.data.latitude, payload.data.longitude,\
        payload.data.height, payload.data.length,\
             case when payload.data.Metal=0 then 'Plastic'\
                  when payload.data.Metal=1 then 'Partial Metal'\
                  when payload.data.Metal=2 then 'Metal' \
                  end as Type_of_Material,\
             case when payload.data.depth<=3 then 'Surfaced'\
                  when payload.data.depth>3 then 'Buried'\
                  end as Depth \
             from MinedSensorTable\
             where payload.data.confidence<=2")
       fldf.show()
       
     Objects with depth greater than 3 are buried and others are surfaced.
     

  

 5.  Next all the land mine locations are displayed with their features. All these objects have confidence greater than 2.Apart from normal depth, height and material features, a new column ‘Alarm_Status’ is added which displayed the status of the mine. For mines with confidence level 6 and high Nitrogen levels, Status is ‘High Alarm’. For mines with Nitrogen level <6 and high Nitrogen level, status is ‘Moderate Alarm’ and rest are considered low alarm.

   spark.sql("select payload.data.latitude, payload.data.longitude,\
             payload.data.height, payload.data.length,\
             case when payload.data.Metal=0 then 'Plastic'\
                  when payload.data.Metal=1 then 'Partial Metal'\
                  when payload.data.Metal=2 then 'Metal' \
                  end as Type_of_Material,\
             case when payload.data.depth<=3 then 'Surfaced'\
                  when payload.data.depth>3 then 'Buried'\
                  end as Depth,\
            case when payload.data.confidence=6 and payload.data.nitrogenLevel='high' then 'High Alarm'\
                 when payload.data.confidence<6 and payload.data.nitrogenLevel='high' then 'Moderate Alarm'\
                 when payload.data.confidence<6 and payload.data.nitrogenLevel='low' then 'Low Alarm'\
                 else 'Insufficient Data' end as Alarm_Status\
            from MinedSensorTable\
            where payload.data.confidence>2\
            order by payload.data.latitude, payload.data.longitude")

  Next, a new column ‘Mine_status’ is added which displays action to be taken based on the ‘Alarm_Status’. 

  lmdf=lmdf.withColumn('Mine_Status',mine_udf(lmdf.Alarm_Status))

   I have created below Spark UDF to return the value of this column :

   mine_udf = udf(lambda alarm:{'High Alarm': 'ALERT:Start Detonation','Moderate Alarm': 'Start Detonation after High Alarm'}.get(alarm, 'More data needed'), StringType())



    I have created a Hive Table using hiveContext in spark as we don’t have Hive installed on AWS due to memory constraints. This is to persist data and I display data from this table as ‘List of Mines’. I have persisted data so that old locations can also be displayed. It is created inside the default ‘spark-warehouse’ folder as Hive is not installed.
       spark.sql("use iot")
       lmdf.write.mode("append").insertInto("MineSensorData")
       hvdf=spark.sql("select * from MineSensorData")
       hvdf.show()


 
  



   I have used folium to map all the latitudes and longitudes on Map. The map is saved in the home directory. The map displays the latitude, longitude and Mine Status. This data is the persisted data from the Hive table ‘MineSensorData’ so that it displays all the new and old locations.


       print("..............Generating Map....................\n")
        
       loc=hvdf.toPandas()

       map_hooray = folium.Map([13.820000,109.000000],zoom_start = 10)
       for i in range(0,len(loc)):
           pop_up= loc['mine_status'][i] +'\n'+'lat:'+str(round(loc['lati         tude'][i],6))+'\n'+'long:'+str(round(loc['longitude'][i],6))

folium.Marker([loc['latitude'][i],loc['longitude'][i]],popup=pop_up).add_to(map_hooray)
       map_hooray.save("MinesLocation.html")
       print('Map saved in the home directory')





Finally, I have generated a Summary Report which shows Total messages, number of high, moderate and low priority mines. I have used global variables for these parameters.

   global ObservationCount
         global HighAlarmCount
      global ModerateAlarmCount
      global LowAlarmCount
      global FalseAlarmCount
   
   HighAlarmCount+=lmdf.filter("Alarm_Status=='High Alarm'").count()
ModerateAlarmCount+= lmdf.filter("Alarm_Status=='Moderate  Alarm'").count()
      LowAlarmCount+= lmdf.filter("Alarm_Status=='Low Alarm'").count()
      FalseAlarmCount+=fldf.count()
      ObservationCount+=jsonRDD.count()











