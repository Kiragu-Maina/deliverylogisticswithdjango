import mysql.connector
import pandas as pd

import json


def convert_xls_to_sql(filename):
    # Load the XLS file into a pandas DataFrame
    df = pd.read_excel(filename, header=1)
    df = df.fillna('')
    df = df.rename(columns={
    'Customer Name ': 'Customer_Name',
    'Posting Description': 'Posting_Description',
    'Route Plan': 'Route_Plan',
    'Ordered Weight': 'Ordered_Weight'
    })

    # Save the DataFrame to a JSON file
    with open('output2.json', 'w') as f:
        json.dump(df.to_dict(orient='records'), f, indent=4)

    # Connect to the MySQL database

    with mysql.connector.connect(
        host="jongleurs.mysql.pythonanywhere-services.com",
        user="jongleurs",
        password="kenchicdb",
        database="jongleurs$kenchic"
    ) as conn:
        # Create a cursor object
        with conn.cursor() as cur:
            # Drop the existing pages_kenchiccnew table (if it exists)
            cur.execute("DROP TABLE IF EXISTS pages_kenchiccnew;")

            # Create a new pages_kenchiccnew table with the appropriate columns
            cur.execute("""
                CREATE TABLE `pages_kenchiccnew` (
                  `id` int NOT NULL AUTO_INCREMENT,
                  `Customer_Name` varchar(100) DEFAULT NULL,
                  `Posting_Description` varchar(100) DEFAULT NULL,
                  `Route_Plan` varchar(100) DEFAULT NULL,
                  `Ordered_Weight` varchar(150) DEFAULT NULL,
                  PRIMARY KEY (`id`)
                );
            """)

            # Loop through the data and generate SQL INSERT statements for each row
            for row in df.itertuples():
                customer_name = row.Customer_Name

                posting_description = row.Posting_Description
                route_plan = row.Route_Plan
                ordered_weight = row.Ordered_Weight
                insert_sql = f'INSERT INTO `pages_kenchiccnew` (`Customer_Name`,`Posting_Description`,`Route_Plan`,`Ordered_Weight`) VALUES ("{customer_name}","{posting_description}","{route_plan}","{ordered_weight}");'
                # select_sql = 'SELECT * FROM pages_kenchiccnew;'


                cur.execute(insert_sql)
                # select = cur.execute(select_sql)
                # print(select)


        conn.commit()
        cur.close()
        conn.close()



    print('routes updated')