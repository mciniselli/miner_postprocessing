import json
import os
import sys

from utils.input_output import write_file

import codecs
'''
get the list of all files
'''

def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)

    return allFiles

'''
given the list of tokens and the index of the first token that is different in before and after code, it returns the start and the end token of the if/for or while condition before that position
'''
def return_condition_extrema(tokens, start_condition):
    num_brackets = 0

    tokens_cond = list()

    for i, token in enumerate(tokens[start_condition + 1:]):
        if token == "(":
            num_brackets += 1
        elif token == ")":
            num_brackets -= 1

        tokens_cond.append(token)

        if num_brackets == 0:
            # print(tokens[start_condition+1:start_condition+i+1])
            return start_condition + i + 1
'''
check if the method is valid.
We check if the only difference is inside a if, for or while condition
'''
def check_record(record, save_path):
    data = json.loads(record)

    tokens_before = data["before"]
    tokens_after = data["after"]
    tokens_before = eval(tokens_before)
    tokens_after = eval(tokens_after)

    tokens_before = [t.strip() for t in tokens_before]
    tokens_after = [t.strip() for t in tokens_after]

    a = len(tokens_before)
    # remove if there exists special tokens
    to_remove = ["|||CONDITION___START|||", "|||CONDITION___END|||"]

    tokens_before = [t for t in tokens_before if t not in to_remove]
    tokens_after = [t for t in tokens_after if t not in to_remove]

    if len(tokens_before) != a:
        print("FFF")

    different_token = -1

    list_conditions = ["if", "for", "while", "else if"]

    for i, (x, y) in enumerate(zip(tokens_before, tokens_after)):
        if x != y:
            different_token = i
            break

    if different_token == -1:
        return

    end_before = -1
    end_after = -1

    start_condition = -1

    for l in range(different_token, 0, -1):
        if tokens_before[l] in list_conditions:
            start_condition = l
            end_before = return_condition_extrema(tokens_before, l) #find the end of the condition for before code
            end_after = return_condition_extrema(tokens_after, l) # find the end of the condition for after code
            break

    if end_before == -1 or end_after == -1:
        return

    if start_condition == -1:
        return

    error = False

    if " ".join(tokens_before[start_condition:end_before]) == " ".join(tokens_after[start_condition:end_after]):
        # print("ERROR")
        error = True

    if " ".join(tokens_before[end_before:]) != " ".join(tokens_after[end_after:]):
        # print("ERROR")
        error = True

    # if error:
    #     print(" ".join(tokens_before[l:end_before]))
    #     print(" ".join(tokens_after[l:end_after]))
    #     print(" ".join(tokens_before[end_before:]))
    #     print(" ".join(tokens_after[end_after:]))
    #     print(tokens_before)
    #     print(tokens_after)
    #     print(different_token)
    #     print(tokens_before[different_token-3:different_token+3])
    #     print(start_condition)
    #     print(end_before)
    #     print(end_after)
    #
    #     url=data["URL"]
    #     url=url.replace("api.", "").replace("/repos", "").replace("/commits/", "/commit/")
    #     # "https://api.github.com/repos/usbong/usbong_pagtsing/commits/70f2422df5dc33859cd33c78863e8f9402a1c3f6"
    #     print(url)

    if error:
        print("AAA")
        return

    data["before"] = str(tokens_before)
    data["after"] = str(tokens_after)
    data["mask_before_index"] = "{} {}".format(start_condition + 1, end_before - 1)
    data["mask_after_index"] = "{} {}".format(start_condition + 1, end_after - 1)
    data["len_before"] = "{}".format(len(tokens_before))
    data["len_after"] = "{}".format(len(tokens_after))

    try:
        with codecs.open(save_path, 'a+', encoding='utf-8') as outfile:
            json.dump(data, outfile)
            outfile.write('\n')
    except Exception as e:
        print(e)
        print(data)


def remove_wrong_records(java_files):
    path_remove_wrong_records = "data/miner_postprocessing/remove_wrong_records"

    if os.path.exists(path_remove_wrong_records) == False:
        os.makedirs(path_remove_wrong_records)

    files = os.listdir(path_remove_wrong_records)
    for f in files:
        os.remove(os.path.join(path_remove_wrong_records, f))

    for file_name in java_files:
        with open(file_name) as f:
            for line in f:
                check_record(line, os.path.join(path_remove_wrong_records, "result.txt"))


def remove_longer_methods(max_len):
    path_remove_longer_methods = "data/miner_postprocessing/remove_longer_methods"

    if os.path.exists(path_remove_longer_methods) == False:
        os.makedirs(path_remove_longer_methods)

    files = os.listdir(path_remove_longer_methods)
    for f in files:
        os.remove(os.path.join(path_remove_longer_methods, f))

    records_path = "data/miner_postprocessing/remove_wrong_records/result.txt"
    save_path = "data/miner_postprocessing/remove_longer_methods/result.txt"
    with open(records_path) as f:
        for line in f:
            data = json.loads(line)

            if int(data["len_before"]) > 100 or int(data["len_after"]) > 100:
                continue

            with open(save_path, 'a+') as outfile:
                json.dump(data, outfile)
                outfile.write('\n')


def remove_duplicates():
    path_remove_duplicates = "data/miner_postprocessing/remove_duplicates"

    if os.path.exists(path_remove_duplicates) == False:
        os.makedirs(path_remove_duplicates)

    files = os.listdir(path_remove_duplicates)
    for f in files:
        os.remove(os.path.join(path_remove_duplicates, f))

    records_path = "data/miner_postprocessing/remove_longer_methods/result.txt"
    save_path = "data/miner_postprocessing/remove_duplicates/result.txt"

    commits = list()
    dict_positions = dict()

    lines = list()

    with open(records_path) as f:
        for i, line in enumerate(f):
            lines.append(line)
            data = json.loads(line)
            commit_id = data["id_commit"]
            commits.append(commit_id)

            if commit_id not in dict_positions.keys():
                l = list()
                l.append(i)
                dict_positions[commit_id] = l
            else:
                l = dict_positions[commit_id]
                l.append(i)
                dict_positions[commit_id] = l



    for k in dict_positions.keys():
        item = dict_positions[k][
            0]  # only first item for each commit_id (i checked and the message for all the records was the same)
        data = json.loads(lines[item])

        with open(save_path, 'a+') as outfile:
            json.dump(data, outfile)
            outfile.write('\n')


'''
    data = {}
    data["id_internal"] = id_internal
    data["tot_processed"] = tot_processed
    data["before"] = before
    data["after"] = after
    data["id_commit"] = id_commit
    data["repo"] = repo
    data["date_commit"] = date_commit
    data["before_api"] = before_api
    data["after_api"] = after_api
    data["URL"] = URL
    data["message"] = message
    data["file_path"] = file_path
    data["mask_before_index"] = "{} {}".format(start_condition + 1, end_before - 1)
    data["mask_after_index"] = "{} {}".format(start_condition + 1, end_after - 1)
    data["len_before"] = "{}".format(len(tokens_before))
    data["len_after"] = "{}".format(len(tokens_after))
'''

def export_files_masked():

    path_export_files_masked = "data/miner_postprocessing/export_files_masked"

    if os.path.exists(path_export_files_masked) == False:
        os.makedirs(path_export_files_masked)

    files = os.listdir(path_export_files_masked)
    for f in files:
        os.remove(os.path.join(path_export_files_masked, f))

    records_path = "data/miner_postprocessing/remove_duplicates/result.txt"

    fields_to_export=["id_internal", "id_commit", "repo"]

    for field in fields_to_export:
        list_to_export=list()
        with open(records_path) as f:
            for line in f:
                data = json.loads(line)
                list_to_export.append(data[field])
                
        write_file(os.path.join(path_export_files_masked, "{}.txt".format(field)), list_to_export)

    list_masked_code=list()
    list_mask_before=list()
    list_mask_after=list()

    with open(records_path) as f:
        for line in f:
            data=json.loads(line)
            before_code=eval(data["before"])
            before_index=data["mask_before_index"].split(" ")
            start_before=int(before_index[0])
            end_before=int(before_index[1])

            after_code=eval(data["after"])
            after_index = data["mask_after_index"].split(" ")
            start_after = int(after_index[0])
            end_after = int(after_index[1])
            masked_before=" ".join(before_code[:start_before+1])+" <x> " + " ".join(before_code[end_before+1:])
            masked_after=" ".join(after_code[:start_after+1])+" <x> " + " ".join(after_code[end_after+1:])

            if masked_before != masked_after: # it should not happen
                print("ERROR")

            mask_before=" ".join(before_code[start_before+1:end_before+1]) + "<z>"
            mask_after=" ".join(after_code[start_after+1:end_after+1]) + "<z>"

            list_masked_code.append(masked_before)
            list_mask_before.append(mask_before)
            list_mask_after.append(mask_after)

    write_file(os.path.join(path_export_files_masked, "{}.txt".format("masked_code")), list_masked_code)
    write_file(os.path.join(path_export_files_masked, "{}.txt".format("mask_before")), list_mask_before)
    write_file(os.path.join(path_export_files_masked, "{}.txt".format("mask_after")), list_mask_after)


def main():
    print("start mining")

    files = getListOfFiles("data/condition_bugfix")

    java_files = [f for f in files if f.endswith(".txt")]
    print(java_files)

    # remove_wrong_records(java_files)
    # remove_longer_methods(100)
    #
    # remove_duplicates()

    # export_files_masked()

if __name__ == "__main__":
    main()
