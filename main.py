import json
import os
import sys

from utils.input_output import write_file
from utils.utilities import *

from utils.textprocessing import TextProcessing

from utils.input_output import *

import codecs

import requests

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

    tokens_before.append("}")
    tokens_after.append("}")

    tokens_before = [t.strip() for t in tokens_before]
    tokens_after = [t.strip() for t in tokens_after]

    tokens_before = [t for t in tokens_before if len(t)>0]
    tokens_after = [t for t in tokens_after if len(t)>0]

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

    return os.path.join(path_remove_wrong_records, "result.txt")

def remove_longer_methods(max_len, input_file):
    path_remove_longer_methods = "data/miner_postprocessing/remove_longer_methods"

    if os.path.exists(path_remove_longer_methods) == False:
        os.makedirs(path_remove_longer_methods)

    files = os.listdir(path_remove_longer_methods)
    for f in files:
        os.remove(os.path.join(path_remove_longer_methods, f))

    # records_path = "data/miner_postprocessing/remove_wrong_records/result.txt"
    records_path=input_file
    save_path = "data/miner_postprocessing/remove_longer_methods/result.txt"
    with open(records_path) as f:
        for line in f:
            data = json.loads(line)

            if int(data["len_before"]) > max_len or int(data["len_after"]) > max_len:
                continue


            with open(save_path, 'a+') as outfile:
                json.dump(data, outfile)
                outfile.write('\n')

    return save_path

def remove_duplicates(input_file):
    path_remove_duplicates = "data/miner_postprocessing/remove_duplicates"

    if os.path.exists(path_remove_duplicates) == False:
        os.makedirs(path_remove_duplicates)

    files = os.listdir(path_remove_duplicates)
    for f in files:
        os.remove(os.path.join(path_remove_duplicates, f))

    # records_path = "data/miner_postprocessing/remove_longer_methods/result.txt"
    records_path=input_file
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

    return save_path

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

def export_files_masked(input_file):

    path_export_files_masked = "data/miner_postprocessing/export_files_masked"

    if os.path.exists(path_export_files_masked) == False:
        os.makedirs(path_export_files_masked)

    files = os.listdir(path_export_files_masked)
    for f in files:
        os.remove(os.path.join(path_export_files_masked, f))

    # records_path = "data/miner_postprocessing/remove_duplicates/result.txt"
    records_path=input_file

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
            # masked_before=" ".join(before_code[:start_before+1])+" <x>" + " ".join(before_code[end_before+1:])
            # masked_after=" ".join(after_code[:start_after+1])+" <x>" + " ".join(after_code[end_after+1:])

            masked_bef_1, index_bef_1 = return_code(before_code[:start_before+1], data["before_code"], False)
            masked_bef_2, index_bef_2=return_code(before_code[end_before+1:], data["before_code"], True)

            masked_before= masked_bef_1 +" <x>" + masked_bef_2

            masked_aft_1, index_aft_1=return_code(after_code[:start_after+1], data["after_code"], False)
            masked_aft_2, index_aft_2=return_code(after_code[end_after+1:], data["after_code"], True)

            masked_after= masked_aft_1 +" <x>" + masked_aft_2


            if masked_before != masked_after: # it should not happen (only some cases when the developer changed the spaces out of the if while or loop)
                print("ERROR")

            # mask_before=" ".join(before_code[start_before+1:end_before+1]) + "<z>"
            # mask_after=" ".join(after_code[start_after+1:end_after+1]) + "<z>"
            mask_before=data["before_code"][index_bef_1:index_bef_2] + "<z>"
            mask_after=data["after_code"][index_aft_1:index_aft_2] + "<z>"


            # mask_before= return_code(before_code[start_before+1::end_before+1], data["before_code"], False)+ "<z>"
            # mask_after= return_code(after_code[start_after+1::end_after+1], data["after_code"], False)+ "<z>"

            list_masked_code.append(masked_before)
            list_mask_before.append(mask_before)
            list_mask_after.append(mask_after)

    write_file(os.path.join(path_export_files_masked, "{}.txt".format("masked_code")), list_masked_code)
    write_file(os.path.join(path_export_files_masked, "{}.txt".format("mask_before")), list_mask_before)
    write_file(os.path.join(path_export_files_masked, "{}.txt".format("mask_after")), list_mask_after)

def return_code(tokens, text, reverse):

    if reverse==False:

        text_new=text
        for t in tokens:
            text_new=text_new.replace(t, " "*(len(t)), 1)

        for i, t in enumerate(text_new):
            if t!=" ":
                return text[:i].strip(), i
    else:

        text_new = text[::-1]
        for t in tokens[::-1]:
            text_new = text_new.replace(t[::-1], " " *(len(t)), 1)

        for i, t in enumerate(text_new):
            if t != " ":
                return text[::-1][:i][::-1].strip(), len(text)-i


def add_original_code(input_file):

    records=read_file(input_file)

    path_add_original_code = "data/miner_postprocessing/add_original_code"

    if os.path.exists(path_add_original_code) == False:
        os.makedirs(path_add_original_code)

    files = os.listdir(path_add_original_code)
    for f in files:
        os.remove(os.path.join(path_add_original_code, f))


    save_path = "data/miner_postprocessing/add_original_code/result.txt"

    for i, r in enumerate(records):
        print()
        data=json.loads(r)
        print("{} out of {}".format(i, len(records)))
        #before
        URL=data["before_api"]

        response = requests.get(url=URL)

        code = (response.content).decode("utf-8")

        write_file("code.java", [code])

        java_path = os.path.join(os.getcwd(), "code.java")
        xml_path = os.path.join(os.getcwd(), "code.xml")

        run_command("srcml {} -o {}".format(java_path, xml_path), os.getcwd())

        f = open(xml_path, "r")
        textxml = ""
        skip_line = True
        for x in f:
            # print(x)
            if skip_line == True:
                skip_line = False
                continue
            if len(x.strip()) == 0:
                continue
            textxml += x.strip() + " "

        f.close()

        t=TextProcessing(textxml)
        t.remove_comments()
        t.remove_tags()

        text_no_tab=(t.text).replace("\t", " ")
        tokens_temp=text_no_tab.split("|_|")

        tokens_with_spaces=list()
        for t in tokens_temp:
            if len(t) == 0:
                continue
            if t==" ":
                tokens_with_spaces.append(t)
            elif t[0]==" " and t[-1]==" ":
                tokens_with_spaces.append(" ")
                tokens_with_spaces.append(t.strip())
                tokens_with_spaces.append(" ")

            elif t[0]==" ":
                tokens_with_spaces.append(" ")
                tokens_with_spaces.append(t.strip())
            elif t[-1] == " ":
                tokens_with_spaces.append(t.strip())
                tokens_with_spaces.append(" ")
            else:
                tokens_with_spaces.append(t)

        tokens_with_spaces=[t for t in tokens_with_spaces if len(t)>0]
        # print(tokens_with_spaces)

        tokens=eval(data["before"])
        # print(" ".join(tokens))
        before_code=check_if_equal(tokens, tokens_with_spaces, i)

        data["before_code"]=before_code

        # after
        URL = data["after_api"]

        response = requests.get(url=URL)

        code = (response.content).decode("utf-8")

        write_file("code.java", [code])

        java_path = os.path.join(os.getcwd(), "code.java")
        xml_path = os.path.join(os.getcwd(), "code.xml")

        run_command("srcml {} -o {}".format(java_path, xml_path), os.getcwd())

        f = open(xml_path, "r")
        textxml = ""
        skip_line = True
        for x in f:
            # print(x)
            if skip_line == True:
                skip_line = False
                continue
            if len(x.strip()) == 0:
                continue
            textxml += x.strip() + " "

        f.close()

        t = TextProcessing(textxml)
        t.remove_comments()
        t.remove_tags()

        tokens_temp = t.text.split("|_|")
        write_file("ccc.txt", tokens_temp)
        tokens_with_spaces = list()
        for t in tokens_temp:
            if len(t) == 0:
                continue
            if t==" ":
                tokens_with_spaces.append(t)
            elif t[0]==" " and t[-1]==" ":
                tokens_with_spaces.append(" ")
                tokens_with_spaces.append(t.strip())
                tokens_with_spaces.append(" ")

            elif t[0]==" ":
                tokens_with_spaces.append(" ")
                tokens_with_spaces.append(t.strip())
            elif t[-1] == " ":
                tokens_with_spaces.append(t.strip())
                tokens_with_spaces.append(" ")
            else:
                tokens_with_spaces.append(t)

        tokens_with_spaces = [t for t in tokens_with_spaces if len(t) > 0]
        # print(tokens_with_spaces)

        tokens = eval(data["after"])
        # print(" ".join(tokens))
        after_code = check_if_equal(tokens, tokens_with_spaces, i)

        data["after_code"] = after_code

        # if we're not able to get the original code we skip the iteration
        # it is generally due to a wrong method that was wrongly cut so that it does not finish with a } (so it is not correct)
        if after_code==None or before_code==None:
            print(i)
            continue
        with open(save_path, 'a+') as outfile:
            json.dump(data, outfile)
            outfile.write('\n')


def check_if_equal(tokens, tokens_with_spaces, index):

    num_tokens_with_spaces=len(tokens_with_spaces)

    index_tokens_not_empty=list()
    for i, t in enumerate(tokens_with_spaces):
        if t != " ":
            index_tokens_not_empty.append(i)

    for start in range(num_tokens_with_spaces):
        curr_index=0
        breaked=False
        for i, k in enumerate(tokens):

            if start+curr_index not in index_tokens_not_empty:
                if curr_index==0:
                    breaked=True
                    break
                curr_index+=1
            if k != tokens_with_spaces[start+curr_index]:
                breaked=True
                break
            else:
                a=1
            curr_index+=1
        if breaked==False:
            return "".join(tokens_with_spaces[start:start+curr_index])

    if (1==1):
        write_file("aaa_{}.txt".format(index), tokens)
        write_file("bbb_{}.txt".format(index), tokens_with_spaces)
        a=1
        return None



def main():
    print("start mining")

    files = getListOfFiles("data/condition_bugfix")

    java_files = [f for f in files if f.endswith(".txt")]
    print(java_files)

    output=""

    # output=remove_wrong_records(java_files)
    # output=remove_longer_methods(150, output)
    #
    # output=remove_duplicates(output)
    #
    # add_original_code("data/miner_postprocessing/remove_duplicates/result.txt")

    export_files_masked("data/miner_postprocessing/add_original_code/result.txt")



if __name__ == "__main__":
    main()
