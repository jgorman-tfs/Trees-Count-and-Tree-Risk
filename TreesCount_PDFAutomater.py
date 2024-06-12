#Created by Joe Gorman: 10/20/2023
#This code uses pdfplumber to read through multiple pdf's in a folder, extract pertenant information for the Trees Count and Trees Risk
#including Date, Coordinates, Number of Trees, and name to the Sharepoint link for each pdf. PDF's are pre-processed to 
#exclude duplicates. PDF's are copied from the sharepoint to preserve original reports, and placed into a PDF Processor folder. 
#The final excel file is then inspected and data is added into the TreesCount or TreesRisk Excel file, which is then read by the TreesCountRisk
#python file in ArcGIS Pro to convert excel data into points. 
from datetime import datetime, timedelta
import pdfplumber
import os
import re
import pandas as pd
import openpyxl
#initialize variables
pdf_directory = 'D:\ArcGIS_Projects\TreesCount\Code\Data\PDFProcessor'
#empty dict for final excel output
data = []
#variables to combine that creates a link to the sharepoint report
base_url = "https://texasforestservice.sharepoint.com/sites/Share-ForestAnalytics/Documents/Geospatial Systems/Texas Forest Info/TreesCount/"
html_start = "<a href = "
html_end = ">Click Here </a>"
apos = "'"

#run through the folder and look for pdfs
for pdf_file in os.listdir(pdf_directory):
    if pdf_file.endswith('.pdf'):
        pdf_file_path = os.path.join(pdf_directory, pdf_file)

        with pdfplumber.open(pdf_file_path) as pdf:
            file_name = os.path.basename(pdf_file)
            if "Risk" in file_name:
                PDFType = "TreeRisk"
                print("Tree Risk")
            else:
                PDFType = "TreeCount"
                print("Tree Count")                                          #get the base name for link
            file_name_sharepoint = html_start + apos + base_url + file_name + apos + html_end   #create the link in html format
            file_date = file_name[:8]                                                           #get the date from the file as YYYYMMdd format
            date_object = datetime.strptime(file_date, "%Y%m%d").date()                         #convert to a YMd format
            day_before = date_object - timedelta(days=1)                                        #get the date of the day prior - some reports come in slow

            month = date_object.strftime("%m").lstrip('0')                                      #get the month, without leading zeros. (ex. 09/23 = 9/23)
            day = date_object.strftime("%d").lstrip("0")                                        #get the day, without leading zeros
            date_string = f"{month}/{day}"                                                      #create a d/M format - most of what is found in the reports
            backwards_date_string = f"{day}/{month}"                                            #some countries use a M/d format

            month_daybefore = day_before.strftime("%m").lstrip('0')                             #This section does the same as above, but for the day before
            day_daybefore = day_before.strftime("%d").lstrip("0")
            day_before_string = f"{month_daybefore}/{day_daybefore}"
            backwards_day_before_string = f"{day_daybefore}/{month_daybefore}"

            float_pattern = r"-?\d{1,3}\.\d{3,}"                                                 #this code find the first coordinate pair in the report
            count = 0                                                                            #initialize count for trees
            first_float = None                                                                   #this is the X coordinate
            second_float = None                                                                  #Y Coordinate

            for page in pdf.pages:
                text = page.extract_text()

                if date_string in text:                                                           #this section uses the dates from the filename to count the number of reports 
                    count += text.count(date_string)                                               #in the pdf, which will equal the number of trees for that day
                elif count == 0 and day_before_string in text:
                    count += text.count(day_before_string)
                elif count == 0 and backwards_date_string in text:
                    count += text.count(backwards_date_string)
                elif count == 0 and backwards_day_before_string in text:
                    count += text.count(backwards_day_before_string)

                if page.page_number == 2:                                                           #Only need to find the float pattern on the second page
                    float_matches = re.findall(float_pattern, text)

                    if len(float_matches) >= 2:
                        first_float = float_matches[0]
                        second_float = float_matches[1]

            # Append the data to the list
            data.append({
                "Date": date_object,
                "Count": count,
                "Xcoord": first_float,
                "Ycoord": second_float,
                "File Name": file_name_sharepoint
            })

df = pd.DataFrame(data)

current_date = datetime.now()
current_date_str = current_date.strftime("%Y%m%d")

# Specify the Excel file path
excel_file = r'D:\ArcGIS_Projects\TreesCount\Code\Data\output_{}.xlsx'.format(current_date_str + PDFType)  # Change this to your desired Excel file name

df.to_excel(excel_file, index=False)

print("Done")