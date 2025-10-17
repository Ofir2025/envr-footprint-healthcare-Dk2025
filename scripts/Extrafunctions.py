
import pandas as pd

def calculate_healthcare_totals(file_path):
    # Load the Excel file with a 3-row header
    df = pd.read_excel(file_path, header=[0, 1, 2], engine='openpyxl')

    # Clean up the MultiIndex column names
    df.columns = pd.MultiIndex.from_tuples([
        tuple(str(level).strip() for level in col)
        for col in df.columns
    ])

    # Define the keys for each category
    hc51_keys = [
        ("Household consumption (Transaction code 3110)", "Pharmaceutical products and other medical products", "06112"),
        ("Marketed individual government consumption (Transaction code 3141)", "Pharmaceutical products and other medical products", "06112")
    ]

    hc52_keys = [
        ("Household consumption (Transaction code 3110)", "Therapeutic appliances and equipment", "06130"),
        ("Marketed individual government consumption (Transaction code 3141)", "Therapeutic appliances and equipment", "06130"),
        ("Non-market individual government consumption (Transaction code 3142)", "Therapeutic appliances and equipment", "06130")
    ]

    healthcare_services_keys = [
        ("Household consumption (Transaction code 3110)", "Out-patient services", "06200"),
        ("Marketed individual government consumption (Transaction code 3141)", "Out-patient services", "06200"),
        ("Non-market individual government consumption (Transaction code 3142)", "Out-patient services", "06200"),
        ("Household consumption (Transaction code 3110)", "Hospital services", "06300"),
        ("Non-market individual government consumption (Transaction code 3142)", "Hospital services", "06300")
    ]

    # Sum values for each category
    hc51_total = df.loc[:, hc51_keys].sum().sum()
    hc52_total = df.loc[:, hc52_keys].sum().sum()
    healthcare_services_total = df.loc[:, healthcare_services_keys].sum().sum()

    return hc51_total, hc52_total, healthcare_services_total
