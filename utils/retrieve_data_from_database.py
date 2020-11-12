import codecs

import mysql.connector as mysql
from mysql.connector import Error

import string
import os

import json

import sys

host = '127.0.0.1'
port = '3306'
user = 'root'
password = 'matteo.ciniselli'
database = "usi"
ssl_disabled = True


###########################
# UTILITIES               #
###########################

'''
return a connection object
'''

def get_connection():
    return mysql.connect(
        host=host,
        port=port,
        user=user,
        passwd=password,
        database=database
    )


def read_file(filepath):  # read generic file
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.readlines()
        c_ = list()
        for c in content:
            r = c.rstrip("\n").rstrip("\r")
            c_.append(r)

    except Exception as e:
        print("Error ReadFile: " + str(e))
        c_ = []
    return c_


def write_file(filename, list_item):  # write generic file
    file = codecs.open(filename, "w", "utf-8")

    for line in list_item:
        file.write(line + "\n")

    file.close()

###########################
# SELECT QUERY            #
###########################

'''
Read data from database

you can set a field with start and end to filter data with the following where condition
WHERE field >= start and field < end


You can set also a step to set the maximum number of records to retrieve in each query

'''


def read_from_data(table, field, start, end, step):

    connection = get_connection()

    num_chunks = int(end - start) // step

    if int(end - start) % step != 0:
        num_chunks += 1

    result_global = list()

    for i in range(num_chunks):
        start_curr = start + i * step

        end_curr = start + (i + 1) * step
        if end_curr > end:
            end_curr = end

        result = get_chunk_of_data(table, field, start_curr, end_curr, connection)

        if len(result) > 0:
            result_global.extend(result)

    if connection.is_connected():
        connection.close()

    return result_global


'''
this function is called from read_from_data when you want to retrieve data using first where condition
'''


def get_chunk_of_data(table, field, start, end, connection):  # read data from method folder
    result = list()
    try:

        connection = get_connection()

        sql_select_Query = "select * from {} where {}>={} and {} < {} ".format(table, field, start, field, end)
        print(sql_select_Query)
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()

        print(len(records))

        for row in records:
            row_temp = str(row)
            # if there are some not printable characters, we skip the line
            bb = ''
            for char in row_temp:
                if char in string.printable:
                    bb += char
            if len(bb) == len(row_temp):
                result.append(row)
            else:
                print("ROW SKIPPED: {}".format(row))

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if (connection.is_connected()):
            cursor.close()
    return result


'''
this function is called from read_from_data when you want to retrieve data using second where condition
'''



###########################
# EXPORT FUNCTION         #
###########################
'''
this function is used to export data.
if you set a separator you will store all records in record.txt files. Each row in made up of all values, separated by the separator string
separator="|||"
record=(1,2,3)
result="1|||2|||3"

if you set export_in_different_files all records will be saved in different files (one for each fields). The name of the file will be 0.txt, 1.txt, ...
'''


def export_data(records, output_folder, separator):
    if os.path.exists(output_folder) == False:
        os.makedirs(output_folder)

    for r in records:
        list_t = list(r)
        print(type(list_t))
        print(list_t)
        row = separator.join([str(e) for e in list_t])

        data = {}
        data["id_internal"] = str(list_t[0])
        data["tot_processed"] = str(list_t[1])
        data["before"] = str(list_t[2])
        data["after"] = str(list_t[3])
        data["id_commit"] = str(list_t[4])
        data["repo"] = str(list_t[5])
        data["date_commit"] = str(list_t[6])
        data["before_api"] = str(list_t[7])
        data["after_api"] = str(list_t[8])
        data["URL"] = str(list_t[9])
        data["message"] = str(list_t[10])
        data["file_path"] = str(list_t[11])

        with open(os.path.join(output_folder, "result.txt"), 'a+') as outfile:
            json.dump(data, outfile)
            outfile.write('\n')



###########################
# TEST CASES              #
###########################


def select():
    table = "before_after_stored"
    field = "id"
    start = 0
    end = 1500000
    step = 500000
    r = read_from_data(table, field, start, end, step)
    return r


def export_single_file():
    output_folder = "output"
    records = select()
    print(len(records))

    export_data(records, output_folder, "||_||")


def main():

    export_single_file()

if __name__ == "__main__":
    main()
