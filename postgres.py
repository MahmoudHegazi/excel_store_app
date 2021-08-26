
# import the PostgreSQL client for Python
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


# Connect to PostgreSQL DBMS
connection = psycopg2.connect("dbname=inventory user=student password=student");
connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);

# Obtain a DB Cursor

cursor          = connection.cursor();
name_Database   = "inventory";

# Create table statement Master DB will hold excel Files data

sqlCreateDatabase ="""
    CREATE TABLE  IF NOT EXISTS master_db (
    	id SERIAL NOT NULL,
    	filename VARCHAR,
        file_path VARCHAR,
        realname VARCHAR,
        created_date date not null default CURRENT_DATE,
    	PRIMARY KEY (id)
        )
    """



# Create table excel meta hold data about each excel file uploaded
sqlCreateExcelMeta ="""
    CREATE TABLE  IF NOT EXISTS worksheets (
    	id SERIAL NOT NULL,
    	file_id INT NOT NULL,
        file_name VARCHAR,
        sheet_name VARCHAR,
        file_path VARCHAR,
        real_name VARCHAR,
        columns VARCHAR,
    	PRIMARY KEY (id)
        )
    """
def setupdb():
    cursor.execute(sqlCreateDatabase)
    cursor.execute(sqlCreateExcelMeta)
