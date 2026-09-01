# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "c388be50-7662-4217-99c7-ef3401173e52",
# META       "default_lakehouse_name": "gitdatalakehouse",
# META       "default_lakehouse_workspace_id": "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d",
# META       "known_lakehouses": [
# META         {
# META           "id": "c388be50-7662-4217-99c7-ef3401173e52"
# META         }
# META       ]
# META     },
# META     "warehouse": {
# META       "known_warehouses": []
# META     }
# META   }
# META }

# CELL ********************

# Welcome to your new notebook
# Type here in the cell editor to add code!

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import *
from pyspark.sql.types import *

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df = spark.read.format("csv").option("header","true").load("abfss://fabricaena@onelake.dfs.fabric.microsoft.com/gitdatalakehouse.Lakehouse/Files/DatafolderADLS/Return.csv")
display(df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df = spark.read.format("csv").option("header","true").load("Files/DatafolderAdventureWorks_Customers/AdventureWorks_Customers.csv")
# df now is a Spark DataFrame containing CSV data from "Files/DatafolderAdventureWorks_Customers/AdventureWorks_Customers.csv".
display(df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import concat, col, lit, split

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df1 = df.withColumn("Full_Name",concat(col("Prefix"),lit(" "),col("FirstName"),lit(" "),col("LastName")))
display(df1)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df2 = df1.withColumn("Domain",split("EmailAddress","@")[1])
display(df2)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df1.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df2.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import col

df3 = df2.withColumn("CustomerKey", col("CustomerKey").cast("long"))
display(df3)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import col

df4 = df3.withColumn("TotalChildren", col("TotalChildren").cast("long"))
display(df4)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import col, when

df5 = df4.withColumn(
    "MaritalStatus",
    when(col("MaritalStatus") == "M", "Married")
    .when(col("MaritalStatus") == "S", "Single")
    .otherwise(col("MaritalStatus"))
)
display(df5)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import col, when

df6 = df5.withColumn(
    "Gender",
    when(col("Gender") == "M", "Men")
    .when(col("Gender") == "F", "Female")
    .otherwise(col("Gender"))
)
display(df6)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df2.write \
    .format("csv") \
    .mode("append") \
    .option("header", "true") \
    .save("Files/customers")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df6.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("gitdatalakehouse.dbo.customers2026")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

sales = spark.read.format("csv").option("header","true").load("Files/DatafolderAdventureWorks_Sales_2016/AdventureWorks_Sales_2016.csv")
# df now is a Spark DataFrame containing CSV data from "Files/DatafolderAdventureWorks_Sales_2016/AdventureWorks_Sales_2016.csv".
display(sales)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************


# CELL ********************

sales2 = spark.read.format("csv").option("header","true").load("Files/DatafolderAdventureWorks_Sales_2017/AdventureWorks_Sales_2017.csv")
# df now is a Spark DataFrame containing CSV data from "Files/DatafolderAdventureWorks_Sales_2017/AdventureWorks_Sales_2017.csv".
display(sales2)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

new_sale = sales.union(sales2)
display(new_sale)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

new_sale.write.format("delta")\
    .mode("append")\
    .saveAsTable("gitdatalakehouse.dbo.sales")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

new_sale.write \
    .format("csv") \
    .mode("append") \
    .option("header", "true") \
    .save("Files/Sales_man")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

merge_file = spark.read.format("delta")\
    .load("abfss://fabricaena@onelake.dfs.fabric.microsoft.com/gitdatalakehouse.Lakehouse/Tables/dbo/Merge")

display(merge_file)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

merge_file.write.format("delta")\
    .mode("append")\
    .saveAsTable("subcat")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

merge_file.write \
    .format("csv") \
    .mode("append") \
    .option("header", "true") \
    .save("Files/subcat")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

Calendar_new = spark.read.format("csv").option("header","true").load("Files/DatafolderAdventureWorks_Calendar/AdventureWorks_Calendar.csv")
# df now is a Spark DataFrame containing CSV data from "Files/DatafolderAdventureWorks_Calendar/AdventureWorks_Calendar.csv".
display(Calendar_new)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

Calendar_new.write.format("delta")\
    .mode("append")\
    .saveAsTable("Calendar")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

Calendar_new.write \
    .format("csv") \
    .mode("append") \
    .option("header", "true") \
    .save("Files/Calendar_man")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

product_n = spark.read.format("csv").option("header","true").load("Files/DatafolderAdventureWorks_Products/AdventureWorks_Products.csv")
# df now is a Spark DataFrame containing CSV data from "Files/DatafolderAdventureWorks_Products/AdventureWorks_Products.csv".
display(product_n)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import split

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

product_new = product_n.withColumn("ProductSKU", split("ProductSKU","-")[0])
display(product_new)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

product_new.write.format("delta")\
    .mode("overwrite")\
    .saveAsTable("product")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

product_new.write \
    .format("csv") \
    .mode("append") \
    .option("header", "true") \
    .save("Files/product")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

return_new = spark.read.format("csv").option("header","true").load("Files/DatafolderADLS/Return.csv")
# df now is a Spark DataFrame containing CSV data from "Files/DatafolderADLS/Return.csv".
display(return_new)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

return_new.write.format("csv")\
    .mode("append")\
    .saveAsTable("return")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

return_new.write.format("delta")\
    .mode("append")\
    .saveAsTable("returndelta")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
