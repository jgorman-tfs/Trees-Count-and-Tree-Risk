from dataclasses import dataclass
from pathlib import Path
import arcpy
from datetime import datetime, timedelta
import pdfplumber
import os
import re
import pandas as pd

arcpy.env.overwriteOutput = True


@dataclass
class ReportConfig:
    pdf_dir: Path
    base_url: str
    csv_path: str
    xy_feature: str
    target_layer: str
    spatial_ref_wkid: int = 4326


def open_file(path):
    os.startfile(path)


def extract_pdf(config: ReportConfig):
    data = []

    for pdf_file_path in config.pdf_dir.glob("*.pdf"):
        with pdfplumber.open(pdf_file_path) as pdf:
            file_name = pdf_file_path.name
            file_name_sharepoint = f"<a href='{config.base_url}{file_name}'>Click Here</a>"

            file_date = file_name[:8]
            date_object = datetime.strptime(file_date, "%Y%m%d").date()
            day_before = date_object - timedelta(days=1)

            month = date_object.strftime("%m").lstrip("0")
            day = date_object.strftime("%d").lstrip("0")
            date_string = f"{month}/{day}"
            backwards_date_string = f"{day}/{month}"

            month_daybefore = day_before.strftime("%m").lstrip("0")
            day_daybefore = day_before.strftime("%d").lstrip("0")
            day_before_string = f"{month_daybefore}/{day_daybefore}"
            backwards_day_before_string = f"{day_daybefore}/{month_daybefore}"

            float_pattern = r"-?\d{1,3}\.\d{3,}"
            count = 0
            first_float = None
            second_float = None

            for page in pdf.pages:
                text = page.extract_text() or ""

                if date_string in text:
                    count += text.count(date_string)
                elif count == 0 and day_before_string in text:
                    count += text.count(day_before_string)
                elif count == 0 and backwards_date_string in text:
                    count += text.count(backwards_date_string)
                elif count == 0 and backwards_day_before_string in text:
                    count += text.count(backwards_day_before_string)

                if page.page_number == 2:
                    float_matches = re.findall(float_pattern, text)
                    if len(float_matches) >= 2:
                        first_float = float_matches[0]
                        second_float = float_matches[1]

            data.append({
                "DateSub": date_object,
                "Trees": count,
                "Xcoord": second_float,
                "Ycoord": first_float,
                "Report": file_name_sharepoint,
                "FilePath": pdf_file_path
            })

    return pd.DataFrame(data)


def fix_zeros(df: pd.DataFrame) -> pd.DataFrame:
    rows_to_drop = []

    for idx, row in df.iterrows():
        if row["Trees"] == 0:
            print(f"\nOpening file: {row['FilePath']}")
            open_file(row["FilePath"])

            while True:
                user_input = input(
                    "Please enter the correct number of trees (0 to delete the row): "
                ).strip()

                if user_input == "":
                    print("Blank input detected. Please enter a whole number.")
                    continue

                try:
                    new_count = int(user_input)
                    break
                except ValueError:
                    print("Invalid input. Please enter a whole number.")

            if new_count == 0:
                rows_to_drop.append(idx)
            else:
                df.at[idx, "Trees"] = new_count

    if rows_to_drop:
        df = df.drop(index=rows_to_drop)

    return df.drop(columns=["FilePath"], errors="ignore")


def append_AGOL_layer(df: pd.DataFrame, config: ReportConfig) -> None:
    spatial_ref = arcpy.SpatialReference(config.spatial_ref_wkid)

    df.to_csv(config.csv_path, index=False)

    arcpy.management.XYTableToPoint(
        config.csv_path,
        config.xy_feature,
        "Xcoord",
        "Ycoord",
        None,
        spatial_ref
    )

    # arcpy.management.Append(
    #     config.xy_feature,
    #     config.target_layer,
    #     "NO_TEST",
    #     update_geometry="UPDATE_GEOMETRY"
    # )


def process_and_append(config: ReportConfig):
    df = extract_pdf(config)
    df = fix_zeros(df)
    append_AGOL_layer(df, config)
    return df