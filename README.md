# Trees-Count-and-Tree-Risk
This repository contains information related to the monthly report of the Trees Count - Tree Inventory application. <br>
*Last Updated 1/5/26*

## Purpose
Trees Count - Tree Inventory is an app created by Fernando that allows users to mark locations of individual trees, record information about them, and generate reports. When a report is generated in the Trees Count - Tree Inventory application by a user, it will be copied into the sharepoint folder. At the beginning of every month, the Trees Count and Tree Risk instant apps need to be updated with the the reports that were generated. This gives the viewers of the instant apps a sense of where the app is being used and a link to the generated report. <br>
The most abstract part of this is the PDF Automater code. It will iterate through a folder of pdf's, and using the date it was copied into sharepoint, look through the entries for the number of entries for that date. It looks for the first float to record the location, and uses some concatenation to get the URL.

## Key Components
PDFs that are located within each folder in sharepoint: TreesCount and TreeRisk <br>
ArcGIS Pro Notebook extracts information from PDFs and updates the feature layer.
Trees Count and Tree Risk feature classes that are in ArcGIS Online are loaded in the aprx already from AGOL <br>

## Structure 
At the beginning of the month <br>
Delete any duplicates <br>
Run through the TreesCount_TreeRisk script <br>
Edit the instant app to reflect new number of reports and dates <br>
Email the report numbers <br>

## Methodology
Copy all of the PDF's from this month into a folder. Ensure the code is updated with the folder path. <br>
Run through the list of the reports and delete any duplicates. Sometimes reports will be the same just with a couple of trees added. Use your best judgement. <br>
Run the notebook Script. This will generate an excel file that records the file name, location, date, url for the pdf and number of reports for that date <br>
If the script did not find any trees in the PDFs, the script will ask you how many trees are actually in the report. Filling in a 0 will drop the report from the list. Adding the correct number of trees will update the row.
MAKE SURE THE LAYER IS LOADED IN THE MAP FROM AGOL.
Open the instant apps and change the date and number of reports.

Send out the update email with the correct number of reports and date to Mac, Gretchen, Rebekah, Leighton, and CC Brad and Fernando. 
