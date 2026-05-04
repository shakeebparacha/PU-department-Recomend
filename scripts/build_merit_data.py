import re
from pathlib import Path

import pandas as pd
import pdfplumber

BASE_DIR = Path(__file__).resolve().parents[1]
PDF_2023 = BASE_DIR / "Merit-of-Last-Year-2023.pdf"
CSV_2024 = BASE_DIR / "pu-merit-app" / "data" / "merit_data.csv"
OUTPUT_DIR = BASE_DIR / "data"
OUTPUT_FILE = OUTPUT_DIR / "merit_data.csv"

SEMESTER_COLUMNS_WITH_SR = [
    (2, "1st Semester Morning"),
    (3, "1st Semester Evening/Replica/Self Support"),
    (4, "5th Semester Morning"),
    (5, "5th Semester Evening/Replica/Self Support"),
]

SEMESTER_COLUMNS_NO_SR = [
    (1, "1st Semester Morning"),
    (2, "1st Semester Evening/Replica/Self Support"),
    (3, "5th Semester Morning"),
    (4, "5th Semester Evening/Replica/Self Support"),
]

PROGRAM_HINTS = re.compile(r"\b(BS|B\.S|BBA|BSc|B\.Com|Pharm|LLB|DPT|BEDS|B\.Ed|MBBS)\b", re.IGNORECASE)


def normalize_text(value: str) -> str:
    if not value:
        return ""
    text = " ".join(value.replace("\n", " ").split())
    text = re.sub(r"(?<=\d)\s+(?=[\d.])", "", text)
    text = re.sub(r"(?<=\.)\s+(?=\d)", "", text)
    text = re.sub(r"(\d)\s*\.\s*(\d)", r"\1.\2", text)
    return text.strip()


def clean_label(value: str) -> str:
    label = value.lstrip("(").strip()
    if label.endswith(")") and "(" not in label:
        label = label[:-1].strip()
    return label


def parse_value(token: str):
    token = token.replace("%", "").strip()
    token = token.replace("..", ".")
    try:
        value = float(token)
    except ValueError:
        return None
    if value <= 0 or value > 100:
        return None
    return value


def parse_cell(cell_text: str):
    if not cell_text:
        return []
    lines = [normalize_text(line) for line in str(cell_text).split("\n") if str(line).strip()]
    pairs = []
    prefix = None

    for line in lines:
        if line.endswith(":") and not re.search(r"\d", line):
            prefix = line[:-1].strip()
            continue

        matches = list(re.finditer(r"([^:]+?):\s*([0-9][0-9 .]*%?)", line))
        if matches:
            for match in matches:
                label = clean_label(normalize_text(match.group(1)))
                value = parse_value(match.group(2))
                if value is None:
                    continue
                full_label = f"{prefix} - {label}" if prefix else label
                pairs.append((full_label, value))
            continue

        numbers = re.findall(r"\b\d+(?:\.\d+)?\b", line)
        for number in numbers:
            value = parse_value(number)
            if value is None:
                continue
            pairs.append((prefix, value))

    return pairs


def build_department_name(base_department: str, program_label: str):
    if not program_label:
        return base_department
    clean = clean_label(program_label)
    if PROGRAM_HINTS.search(clean):
        return base_department
    return f"{base_department} - {clean}"


def build_program_name(program_label: str):
    clean = clean_label(program_label) if program_label else ""
    if clean and PROGRAM_HINTS.search(clean):
        return clean
    if clean and not PROGRAM_HINTS.search(clean):
        return "BS (Hons.)"
    return "BS (Hons.)"


def extract_2023_rows():
    rows = []
    with pdfplumber.open(PDF_2023) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            page_lines = [line.strip() for line in page_text.splitlines() if line.strip()]
            faculties = [line for line in page_lines if "Faculty of" in line]
            campus_names = []
            for line in page_lines:
                if not line.endswith("Campus"):
                    continue
                if "Q.A." in line or "University of the Punjab" in line:
                    continue
                campus_names.append(line.replace("Campus", "").strip())
            tables = page.extract_tables() or []

            if not tables:
                continue

            if not faculties:
                faculties = ["Unknown"]

            table_meta = []
            if campus_names and len(tables) > 1 and len(faculties) == 1:
                base_faculty = faculties[0]
                table_meta.append((base_faculty, "Main"))
                for campus in campus_names[: len(tables) - 1]:
                    table_meta.append(("Campus Programs", campus))
                while len(table_meta) < len(tables):
                    table_meta.append((base_faculty, "Main"))
            else:
                table_faculties = [faculties[min(idx, len(faculties) - 1)] for idx in range(len(tables))]
                table_meta = [(faculty, "Main") for faculty in table_faculties]

            for table, (faculty, campus) in zip(tables, table_meta):
                if not table or len(table) < 2:
                    continue
                current_department = ""
                header = [normalize_text(cell) for cell in table[0] if cell]
                header_text = " ".join(header)
                if "Sr." in header_text or "Sr" in header_text:
                    department_index = 1
                    semester_columns = SEMESTER_COLUMNS_WITH_SR
                else:
                    department_index = 0
                    semester_columns = SEMESTER_COLUMNS_NO_SR

                for row in table[1:]:
                    if not row or len(row) < 2:
                        continue
                    if department_index >= len(row):
                        continue
                    department_cell = normalize_text(row[department_index])
                    if department_cell:
                        if re.match(r"^[ivxlcdm]+\.|^[a-z]\.", department_cell, re.IGNORECASE):
                            department_cell = f"{current_department} - {department_cell.lstrip('ivxlcdmIVXLCDM. ')}".strip()
                        else:
                            current_department = department_cell
                    else:
                        department_cell = current_department

                    if not department_cell:
                        continue

                    for col_index, semester_label in semester_columns:
                        if col_index >= len(row):
                            continue
                        cell_text = row[col_index]
                        pairs = parse_cell(cell_text)
                        if not pairs:
                            continue
                        for program_label, merit_value in pairs:
                            department_name = build_department_name(department_cell, program_label)
                            program_name = build_program_name(program_label)
                            rows.append({
                                "Year": 2023,
                                "Faculty": faculty.replace("Faculty of ", "").strip(),
                                "Department": department_name,
                                "Program": program_name,
                                "Campus": campus,
                                "Semester_Type": semester_label,
                                "Merit_Percentage": merit_value,
                            })
    return rows


def main():
    rows_2023 = extract_2023_rows()
    if not rows_2023:
        raise SystemExit("No rows extracted from 2023 PDF.")

    df_2023 = pd.DataFrame(rows_2023)

    if CSV_2024.exists():
        df_2024 = pd.read_csv(CSV_2024)
    else:
        df_2024 = pd.DataFrame(columns=df_2023.columns)

    combined = pd.concat([df_2023, df_2024], ignore_index=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_FILE, index=False)
    print(f"Wrote {len(combined)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
