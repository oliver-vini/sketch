import boto3
import os
import psycopg2
import logging
import sys
import argparse


# PSQL DB connection string
# DB_CONN_STRING = os.getenv(
#     'DB_CONN_STRING', 'postgres://postgres:mysecretpassword@172.17.0.3/proddatabase')

# Creating Session With Boto3.
session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

# Creating S3 Resource From the Session.
s3 = session.resource('s3')
source_bucket = 'vini-sketch-legacy-s3'
destination_bucket = 'vini-sketch-prod-s3'

# Connect to db
try:
    connection = psycopg2.connect(user="postgres",
                                  password="mysecretpassword",
                                  host="172.17.0.3",
                                  port="5432",
                                  database="proddatabase")
    cursor = connection.cursor()
    postgreSQL_select_Query = "select * from avatars"

    cursor.execute(postgreSQL_select_Query)
    print("Selecting AWS S3 paths from table avatars")
    s3_path = cursor.fetchall()

    for row in s3_path:
        copy_source = {
            'Bucket': source_bucket,
            'Key': row[1]
        }

        bucket = s3.Bucket(destination_bucket)
        new_row = row[1].split("/")[0]+"_prod" + "/"+row[1].split("/")[1]
        bucket.copy(copy_source, new_row)
        print(new_row)
        print(row[1])

        print("Table Before updating record ")
        sql_select_query = """select * from avatars where path = %s"""
        cursor.execute(sql_select_query, (row[1],))
        record = cursor.fetchone()
        print(record)

        # Update single record now
        sql_update_query = """Update avatars set path = %s where path = %s"""
        cursor.execute(sql_update_query, (new_row, row[1]))
        connection.commit()
        count = cursor.rowcount
        print(count, "Record Updated successfully ")

        print("Table After updating record ")
        sql_select_query = """select * from avatars where path = %s"""
        cursor.execute(sql_select_query, (new_row,))
        record = cursor.fetchone()
        print(record)

        # cursor.execute(
        #     f'UPDATE avatars SET path = {new_row} WHERE path = {row[1]}')

        # cursor.execute(
        #     f'UPDATE avatars SET path = "{new_row}" WHERE path = "{row[1]}"')

        # cursor.execute('UPDATE avatars SET path = ' +
        #                new_row + ' WHERE id = ' + row[1])
        # # cursor.execute(
        # "UPDATE avatars SET path = " + new_row + " WHERE path = " + 'row[1]')

except (Exception, psycopg2.Error) as error:
    print("Error while fetching data from PostgreSQL", error)


# # Creating S3 Resource From the Session.
# s3 = session.resource('s3')

# # Create a Soucre Dictionary That Specifies Bucket Name and Key Name of the Object to Be Copied
# copy_source = {
#     'Bucket': 'vini-sketch-legacy-s3',
#     'Key': 'job_done.jpg'
# }

# bucket = s3.Bucket('vini-sketch-prod-s3')

# bucket.copy(copy_source, 'job_done.jpg')

# # Printing the Information That the File Is Copied.
# print('Single File is copied')
