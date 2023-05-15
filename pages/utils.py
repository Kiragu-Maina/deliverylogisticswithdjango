import pandas as pd
from django.db import connection
import json


def convert_xls_to_sql(filename):
    # Load the XLS file into a pandas DataFrame
    df = pd.read_excel(filename, header=1)
    df = df.fillna("")
    df = df.rename(
        columns={
            "Customer Name ": "Customer_Name",
            "Posting Description": "Posting_Description",
            "Route Plan": "Route_Plan",
            "Ordered Weight": "Ordered_Weight",
        }
    )

    # Save the DataFrame to a JSON file
    with open("output2.json", "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=4)

    # Connect to the PostgreSQL database using Django's database settings
    conn = connection.cursor()

    # Drop the existing pages_kenchiccnew table (if it exists)
    conn.execute("DROP TABLE IF EXISTS pages_kenchiccnew;")

    # Create a new pages_kenchiccnew table with the appropriate columns
    conn.execute(
        """
        CREATE TABLE pages_kenchiccnew (
        id SERIAL PRIMARY KEY,
        Customer_Name varchar(100),
        Posting_Description varchar(100),
        Route_Plan varchar(100),
        Ordered_Weight varchar(150)
        );
    """
    )

    # Loop through the data and generate SQL INSERT statements for each row
    for row in df.itertuples():
        customer_name = row.Customer_Name
        posting_description = row.Posting_Description
        route_plan = row.Route_Plan
        ordered_weight = row.Ordered_Weight
        insert_sql = "INSERT INTO pages_kenchiccnew (Customer_Name, Posting_Description, Route_Plan, Ordered_Weight) VALUES (%s, %s, %s, %s);"
        values = (customer_name, posting_description, route_plan, ordered_weight)
        conn.execute(insert_sql, values)

    connection.commit()

    print("routes updated")
