# Trees-Count-and-Tree-Risk
This repository contains information related to the monthly report of the Trees Count - Tree Inventory application. <br>
*Last Updated 6-24-24*

## Purpose
Trees Count - Tree Inventory is an app created by Fernando that allows users to mark locations of individual trees, record information about them, and generate reports. When a report is generated in the Trees Count - Tree Inventory application by a user, it will be copied into the sharepoint folder. At the beginning of every month, the Trees Count and Tree Risk instant apps need to be updated with the the reports that were generated. This gives the viewers of the instant apps a sense of where the app is being used and a link to the generated report. <br>
The most abstract part of this is the PDF Automater code. It will iterate through a folder of pdf's, and using the date it was copied into sharepoint, look through the entries for the number of entries for that date. It looks for the first float to record the location, and uses some concatenation to get the URL.

## Key Components
PDFs that are located within each folder in sharepoint: TreesCount and TreeRisk <br>
2 python files that used to generate the excel sheets, then map the points in ArcPro with the required attributes <br>
Trees Count and Tree Risk feature classes that are in ArcGIS Online <br>

## Structure 
At the beginning of the month <br>
Delete any duplicates <br>
Generate separate excel files from both folders using the PDF automater script <br>
Make edits as needed <br>
Run the TreeCount script in the TreeCount toolbox in ArcPro <br>
Share and Overwrite the TreesCount and TreeRisk shapefile <br>
Edit the instant app to reflect new number of reports and dates <br>
Email the report numbers <br>

## Methodology
Copy all of the PDF's from this month into a folder. Ensure the code is updated with the folder path. <br>
Run through the list of the reports and delete any duplicates. Sometimes reports will be the same just with a couple of trees added. Use your best judgement. <br>
Run the PDF Script. This will generate an excel file that records the file name, location, date, url for the pdf and number of reports for that date <br>
**Examine the excel file that's generated. You will notice that some of files might have a 0 for count. This means that the code did not see any entries on the day of, the day before, or the day after the report was copied. Soemtimes users will generate reports for inventories that were not neccessarily done that day. These can be deleted from the excel file. Another issue is that users can choose their own date format. So for countries that use formats like MM/DD/YY, the code may skip over it. It's probably possible to fix this issue, but for now just investigate the reports that have a 0 count and use your best judgement on whether to keep it or not.** <br>



