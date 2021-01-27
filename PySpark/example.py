$ sudo apt install default-jre
$ sudo apt install openjdk-11-jre-headless


import os
os.getcwd()
os.environ["SPARK_HOME"]="/home/anaconda3/lib/python3.7/site-packages/pyspark"

import findspark
findspark.init()


import pyspark # only run after findspark.init()
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("PySpark").getOrCreate()
spark

cores = spark._jsc.sc().getExecutorMemoryStatus().keySet().size()
print("You are working with", cores, "core(s)")
spark


data = [['tom', 10], ['nick', 15], ['juli', 14]] 

df = spark.createDataFrame(data,['Name', 'Age']) 

df.show()
############################

path = "/home/anaconda3/work/Python Files and Datasets AS of 22DEC20/PySpark DataFrame Essentials/Datasets/students.csv"
df = spark.read.csv(path,inferSchema=True,header=True)
df.toPandas()

df.groupBy("gender").agg({'math score':'mean'}).show()

df.select("gender", "math_score").summary("count", "min", "max").show()
df.select(['Name','gender']).orderBy('Name').show(5,False) #not truncated
df.select("Name","math_score").where(df.Name.like("A%")).show(5, False)
df[df.Name.isin("L. Messi", "Cristiano Ronaldo")].limit(4).toPandas()
df.select("Photo",df.Photo.substr(-4,4)).show(5,False) #png
df.select("Name","math_score").where(df.name.startswith("L")).where(df.Name.like("A%")).show(5, False)

df.filter("Age>40").limit(4).toPandas()
## spark starts with 1 != Python = 0 
## filer BEFORE select

# It's not until we change the df in some way, that the ID changes
# These kinds of commands won't actually be run...
df = df.withColumn('new_col', df['math score'] * 2)

df2 = df.withColumnRenamed('Rolling year total number of offences','Count')

df = df.withColumn('publish_time_2',regexp_replace(df.publish_time, 'T', ' '))
df = df.withColumn('publish_time_2',regexp_replace(df.publish_time_2, 'Z', ''))
df = df.withColumn("publish_time_3", to_timestamp(df.publish_time_2, 'yyyy-MM-dd HH:mm:ss.SSS'))

from pyspark.sql.functions import year, month
# Other options: dayofmonth, dayofweek, dayofyear, weekofyear
df.select("trending_date",year("trending_date"),month("trending_date")).show(5)

from pyspark.sql.functions import datediff
df.select("trending_date","publish_time_3",(datediff(df.trending_date,df.publish_time_3)/365).alias('diff')).show(5)

df = df.withColumn('title',lower(df.title)) # or rtrim/ltrim
df.select("title").show(5,False)

###### OR

import pyspark.sql.functions as f
df.select("publish_time",f.translate(f.col("publish_time"), "TZ", " ").alias("translate_func")).show(5,False)

df.createOrReplaceTempView("tempview")
spark.sql("SELECT Region, sum(Count) AS Total FROM tempview GROUP BY Region").limit(5).toPandas()
spark.sql("SELECT * FROM tempview WHERE App LIKE '%dating%'").limit(5).toPandas()


print("Option#1: select or withColumn() using when-otherwise")
from pyspark.sql.functions import when
df.select("likes","dislikes",(when(df.likes > df.dislikes, 'Good').when(df.likes < df.dislikes, 'Bad').otherwise('Undetermined')).alias("Favorability")).show(3)

print("Option2: select or withColumn() using expr function")
from pyspark.sql.functions import expr 
df.select("likes","dislikes",expr("CASE WHEN likes > dislikes THEN  'Good' WHEN likes < dislikes THEN 'Bad' ELSE 'Undetermined' END AS Favorability")).show(3)

print("Option 3: selectExpr() using SQL equivalent CASE expression")
df.selectExpr("likes","dislikes","CASE WHEN likes > dislikes THEN  'Good' WHEN likes < dislikes THEN 'Bad' ELSE 'Undetermined' END AS Favorability").show(3)

from pyspark.sql.functions import concat_ws
df.select(concat_ws(' ', df.title,df.channel_title,df.tags).alias('text')).show(1,False)

from pyspark.sql.functions import split
df.select("title").show(1,False)
df.select(split(df.title, ' ').alias('new')).show(1,False)


col_list= df.columns[0:5]
df3=df.select(col_list)



from pyspark.ml.feature import SQLTransformer

sqlTrans = SQLTransformer(
    statement="SELECT PFA,Region,Offence FROM __THIS__") ## placeholder
sqlTrans.transform(df).show(5)

type(sqlTrans)

df4=sqlTrans.transform(df)

from pyspark.sql.functions import expr 

sqlTrans = SQLTransformer(
    statement="SELECT SUM(Count) as Total FROM __THIS__") 
sqlTrans.transform(df).show(5)

df.withColumn("percent",expr("round((count/244720928)*100,2)")).show()
df.select("*",expr("round((count/244720928)*100,2) AS percent")).show()

from pyspark.sql.types import *
df = googlep.withColumn("Rating", googlep["Rating"].cast(FloatType()))  .withColumn("Reviews", googlep["Reviews"].cast(IntegerType()))  .withColumn("Price", googlep["Price"].cast(IntegerType()))
print(df.printSchema())

##### Available types:
#     - DataType
#     - NullType
#     - StringType
#     - BinaryType
#     - BooleanType
#     - DateType
#     - TimestampType
#     - DecimalType
#     - DoubleType
#     - FloatType
#     - ByteType
#     - IntegerType
#     - LongType
#     - ShortType
#     - ArrayType
#     - MapType
#     - StructField
#     - StructType

################################################################################

# Until we executute a command like this
collect = df.collect()

# Even if we duplicate the dataframe, the ID remains the same
df2 = df
df2.rdd.id()

# Iterate over a column

from pyspark.sql.functions import udf
from pyspark.sql.types import IntegerType

def square(x):
    return int(x**2)
square_udf = udf(lambda z: square(z), IntegerType())

df.select('dislikes',square_udf('dislikes').alias('likes_sq')).where(col('dislikes').isNotNull()).show()

#######################################################################

students = spark.read.csv(path+'students.csv',inferSchema=True,header=True)
print(type(students))

studentsPdf = students.toPandas()
print(type(studentsPdf))

students.schema['math score'].dataType

students.describe(['math score']).show()

students.select("math score", "reading score","writing score").summary("count", "min", "25%", "75%", "max").show()

# **Parquet Files**

parquet = spark.read.parquet(path+'users1.parquet')
parquet.show(2)

# **Partitioned Parquet Files**
# Actually most big datasets will be partitioned. Here is how you can collect all the pieces (parts) of the dataset in one simple command.

partitioned = spark.read.parquet(path+'users*')
partitioned.show(2)

users1_2 = spark.read.option("basePath", path).parquet(path+'users1.parquet', path+'users2.parquet')
users1_2.show()

# However you often have to set the schema yourself if you aren't dealing with a .read method that doesn't have inferSchema() built-in.

from pyspark.sql.types import StructField,StringType,IntegerType,StructType,DateType

data_schema = [StructField("name", StringType(), True),
               StructField("email", StringType(), True),
               StructField("city", StringType(), True),
               StructField("mac", StringType(), True),
               StructField("timestamp", DateType(), True),
               StructField("creditcard", StringType(), True)]

final_struc = StructType(fields=data_schema)

people = spark.read.json(path+'people.json', schema=final_struc)

people.printSchema()

# Note the strange naming convention of the output file in the path that you specified. 
# Spark uses Hadoop File Format, which requires data to be partitioned - that's why you have part- files. 
# If you want to rename your written files to a more user friendly format, you can do that using the method below:

from py4j.java_gateway import java_import
java_import(spark._jvm, 'org.apache.hadoop.fs.Path')

fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
file = fs.globStatus(spark._jvm.Path('write_test.csv/part*'))[0].getPath().getName()
fs.rename(spark._jvm.Path('write_test.csv/' + file), spark._jvm.Path('write_test2.csv')) #these two need to be different
fs.delete(spark._jvm.Path('write_test.csv'), True)

# WRITE in Data

students.write.mode("overwrite").csv('write_test.csv')

users1_2.write.mode("overwrite").parquet('parquet/')

users1_2.write.mode("overwrite").partitionBy("gender").parquet('part_parquet/')

