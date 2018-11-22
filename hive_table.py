#This should be run before the kafka-direct-project.py script so that hive table is present to persist the data
from pyspark import SparkContext
from pyspark.sql import HiveContext

if __name__ == "__main__":
 sc = SparkContext(appName="LandMinesSensorAnalysis")
 spark=HiveContext(sc)
 spark.sql("create database iot").show()
 spark.sql("use iot")

 spark.sql("create table MineSensorData(\
           latitude float,\
            longitude float,\
			 height float,\
              length float,\
            Type_of_Material string,\
            Depth float,\
            Alarm string,\
            Mine_status string)")

 spark.sql("show tables").show()