#Author: Joe Gorman
#Date Created: 6/24/23
#Date Last Updated: 6/29/2023
#Purpose: Take data TreesCount and TreeRisk sheets, and plot them in ArcPro with associated report, date, and number of trees surveyed.
#Reports show as a link to the sharepoint

#import modules
import arcpy, os
arcpy.overwriteOutput = True

#get input values
outFC = arcpy.GetParameterAsText(0)
inFile = arcpy.GetParameterAsText(1)
coordsys = arcpy.GetParameterAsText(2)

DateSubmittedFld = "DateSub"
NumberOfTreesFld = "Trees"
ReportFld = "Report"

#set workspace environment and feature class
arcpy.env.workspace = os.path.dirname(outFC)
featClass = os.path.basename(outFC)

#delete the shapefile if it already exists 
if arcpy.Exists(outFC):
    arcpy.Delete_management(outFC)

#create feature class and define its projection
arcpy.CreateFeatureclass_management(arcpy.env.workspace,
                                    featClass, "POINT")
arcpy.DefineProjection_management(featClass, coordsys)

#validate field names
DateSubmittedFld = arcpy.ValidateFieldName(DateSubmittedFld)
NumberOfTreesFld = arcpy.ValidateFieldName(NumberOfTreesFld)

#add fields
arcpy.AddField_management(featClass, DateSubmittedFld, "date", "50")
arcpy.AddField_management(featClass, NumberOfTreesFld, "short", "50")
arcpy.AddField_management(featClass, ReportFld, "text", "100")

#open the csv file and read the lines
TreesCount = open(inFile, 'r', errors = "ignore")
headerLine = TreesCount.readline()
lstValue = headerLine.split(",")
arcpy.AddMessage(lstValue)
#get the index values
xCoordIndex = lstValue.index("LONGITUDE")
yCoordIndex = lstValue.index("LATITUDE")
dateIndex = lstValue.index("DateSub")
treesIndex = lstValue.index("TreesNumber")
reportIndex = lstValue.index("Report")
lines = TreesCount.readlines()
TreesCount.close()
#intialize the counting variable
pid = 1
#Create the list of fields
fieldList = ["FID", "DateSub", "Trees", "SHAPE@", "Report"]
#create the search cursor and set the fields
with arcpy.da.InsertCursor(featClass, fieldList) as isCursor:
#initialize the for loop and retrieve the data based on the index
    for line in lines:
        segment = line.split(",")
        xCoord = float(segment[xCoordIndex])
        yCoord = float(segment[yCoordIndex])
        DateSub = str(segment[dateIndex])
        TreesNumber = float(segment[treesIndex])
        Report = str(segment[reportIndex])
        #Report = '<a href="http://texasforestinfo.com">' + str(segment[reportIndex]) + '</a>'

#add the new point and insert the row
        newPoint = [pid, DateSub, TreesNumber, arcpy.PointGeometry(arcpy.Point(xCoord, yCoord), spatial_reference = 4326), Report]
        isCursor.insertRow(newPoint)
        
        

#add to the counting variable
        pid = pid + 1
        
arcpy.AddMessage("complete")
del isCursor
