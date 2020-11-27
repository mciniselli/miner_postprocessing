import os
import json
import requests

from utils.input_output import read_file, write_file
from utils.utilities import run_command

from utils.textprocessing import TextProcessing


'''
Add code before and code after to the json (the code before is made up by all the tokens but instead of putting a space between each token we put a space only if there is a space in the source code)
'''


def add_original_code(input_file):
    records = read_file(input_file)

    path_add_original_code = "data/miner_postprocessing/add_original_code"

    if os.path.exists(path_add_original_code) == False:
        os.makedirs(path_add_original_code)

    files = os.listdir(path_add_original_code)
    for f in files:
        os.remove(os.path.join(path_add_original_code, f))

    save_path = "data/miner_postprocessing/add_original_code/result.txt"

    for i, r in enumerate(records):
        print()
        data = json.loads(r)
        print("{} out of {}".format(i, len(records)))
        # before
        URL = data["before_api"]

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

        text_no_tab = (t.text).replace("\t", " ")
        tokens_temp = text_no_tab.split("|_|")

        tokens_with_spaces = list()
        for t in tokens_temp:
            if len(t) == 0:
                continue
            if t == " ":
                tokens_with_spaces.append(t)
            elif t[0] == " " and t[-1] == " ":
                tokens_with_spaces.append(" ")
                tokens_with_spaces.append(t.strip())
                tokens_with_spaces.append(" ")

            elif t[0] == " ":
                tokens_with_spaces.append(" ")
                tokens_with_spaces.append(t.strip())
            elif t[-1] == " ":
                tokens_with_spaces.append(t.strip())
                tokens_with_spaces.append(" ")
            else:
                tokens_with_spaces.append(t)

        tokens_with_spaces = [t for t in tokens_with_spaces if len(t) > 0]
        # print(tokens_with_spaces)

        tokens = eval(data["before"])
        # print(" ".join(tokens))
        before_code = check_if_equal(tokens, tokens_with_spaces, i)

        data["before_code"] = before_code

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

        text_no_tab = (t.text).replace("\t", " ")
        tokens_temp = text_no_tab.split("|_|")

        tokens_temp = t.text.split("|_|")
        write_file("ccc.txt", tokens_temp)
        tokens_with_spaces = list()
        for t in tokens_temp:
            if len(t) == 0:
                continue
            if t == " ":
                tokens_with_spaces.append(t)
            elif t[0] == " " and t[-1] == " ":
                tokens_with_spaces.append(" ")
                tokens_with_spaces.append(t.strip())
                tokens_with_spaces.append(" ")

            elif t[0] == " ":
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
        if after_code == None or before_code == None:
            print(i)
            continue
        with open(save_path, 'a+') as outfile:
            json.dump(data, outfile)
            outfile.write('\n')


def check_if_equal(tokens, tokens_with_spaces, index):
    num_tokens_with_spaces = len(tokens_with_spaces)

    index_tokens_not_empty = list()
    for i, t in enumerate(tokens_with_spaces):
        if t != " ":
            index_tokens_not_empty.append(i)

    for start in range(num_tokens_with_spaces):
        curr_index = 0
        breaked = False
        for i, k in enumerate(tokens):

            if start + curr_index not in index_tokens_not_empty:
                if curr_index == 0:
                    breaked = True
                    break
                curr_index += 1
            if k != tokens_with_spaces[start + curr_index]:
                breaked = True
                break
            else:
                a = 1
            curr_index += 1
        if breaked == False:
            return "".join(tokens_with_spaces[start:start + curr_index])

    if (1 == 1):
        write_file("aaa_{}.txt".format(index), tokens)
        write_file("bbb_{}.txt".format(index), tokens_with_spaces)
        a = 1
        return None
