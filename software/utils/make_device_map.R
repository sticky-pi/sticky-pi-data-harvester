# script to run manually to generate a json map of devices
library(jsonlite)
library(data.table)
dt = fread('/tmp/device_map.csv')
l <- as.list(dt[,V2])
names(l) <- dt[,V1]

jsonlite::toJSON(l,auto_unbox=T)

