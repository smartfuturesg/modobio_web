"""
    This script is for running .sql files stored in the database/
    directory. All scripts with the .sql file extension will have 
    comments removed. They will be run in the order they appear in the directory.

    Usage:
    Simply call the file from anywhere and pass the database uri string in to the
    db_uri argument. example:

        python database/sql_scriptrunner.py --db_uri postgresql://postgres:@localhost/modobio

    If no URI is selected through the terminal, this script will search for the 
    following environment variables to construct a URI:

        DB_HOST. DB_USER, DB_PASS
    
    The script will assume the DB name is 'modobio' and the 
    DB flavor is 'postgresql'

"""
import argparse
import glob
import os
import sys

import boto3
from sqlalchemy import create_engine, text


parser = argparse.ArgumentParser(description='')
parser.add_argument('--db_uri', help="db uri" )


if __name__ == "__main__":

    args = parser.parse_args()
    """
    Use the db uri passed in from the terminal
    if not, attempt to find the appropriate
    database connection parameters from env variables

    """
    if args.db_uri:
        DB_URI = args.db_uri
    else: 
        db_user = os.getenv('DB_USER', '')
        db_pass = os.getenv('DB_PASS', '')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_flav = os.getenv('DB_FLAV', 'postgresql')
        db_name = os.getenv('DB_NAME', 'modobio')
    
        DB_URI = f'{db_flav}://{db_user}:{db_pass}@{db_host}/{db_name}'

    print(f"using the following databsae URI. \n \t{DB_URI}\n")
    engine = create_engine(DB_URI)
    current_dir = os.path.realpath(__file__)[:-19]
    sql_files = glob.glob(current_dir+'*.sql')

    
    # run .sql file to create db procedures
    #  read each file, remove comments,
    #  execute raw sql on database
    raw_sql_cleaned = []
    with engine.connect() as conn:
        for sql_script in sql_files:
            script_name = sql_script[len(current_dir)::]
            with open(sql_script, "r") as f:
                raw_sql = f.readlines()
                _raw_sql = [x for x in raw_sql if not x.startswith('--')]
                breakpoint()
                try:
                    conn.execute(text(''.join(_raw_sql)))
                    print(f"{script_name} succeeded")
                except Exception as e:
                    print(e)
                    print(f"\n{script_name} failed for the reasons above")
                    #sys.exit()
                
   
