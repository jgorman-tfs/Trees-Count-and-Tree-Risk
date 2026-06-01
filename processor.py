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

def normalize_date(match: str):
    """
    Try to convert a matched string into a date object.
    Returns None if invalid.
    """

    # YYYYMMDD
    if re.fullmatch(r"\d{8}", match):
        try:
            return datetime.strptime(match, "%Y%m%d").date()
        except ValueError:
            return None

    # M/D/YY or MM/DD/YY or M.D.YY etc.
    if re.fullmatch(r"\d{1,2}[./]\d{1,2}[./]\d{2,4}", match):
        sep = "." if "." in match else "/"
        parts = match.split(sep)

        if len(parts) != 3:
            return None

        m, d, y = parts

        try:
            m = int(m)
            d = int(d)
            y = int(y)

            # assume 2000s only
            if y < 100:
                y += 2000

            return datetime(y, m, d).date()
        except ValueError:
            return None

    return None


def extract_pdf(config: "ReportConfig"):
    data = []

    float_pattern = r"-?\d{1,3}\.\d{3,}"
    date_pattern = r"\b\d{8}\b|\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b"

    for pdf_file_path in config.pdf_dir.glob("*.pdf"):
        with pdfplumber.open(pdf_file_path) as pdf:

            file_name = pdf_file_path.name
            file_name_sharepoint = f"<a href='{config.base_url}{file_name}'>Click Here</a>"

            file_date = datetime.strptime(file_name[:8], "%Y%m%d").date()

            target_year = file_date.year
            target_month = file_date.month

            count = 0
            first_float = None
            second_float = None

            for page in pdf.pages:
                text = page.extract_text() or ""

                # ---- DATE MATCHING LOGIC ----
                candidates = re.findall(date_pattern, text)

                for c in candidates:
                    parsed = normalize_date(c)
                    if not parsed:
                        continue

                    if parsed.year == target_year and parsed.month == target_month:
                        count += 1

                # ---- FLOAT EXTRACTION (unchanged logic) ----
                if page.page_number == 2:
                    float_matches = re.findall(float_pattern, text)
                    if len(float_matches) >= 2:
                        first_float = float_matches[0]
                        second_float = float_matches[1]

            data.append({
                "DateSub": file_date,
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

    arcpy.management.Append(
        config.xy_feature,
        config.target_layer,
        "NO_TEST",
        update_geometry="UPDATE_GEOMETRY"
    )


def process_and_append(config: ReportConfig):
    df = extract_pdf(config)
    df = fix_zeros(df)
    append_AGOL_layer(df, config)
    return df