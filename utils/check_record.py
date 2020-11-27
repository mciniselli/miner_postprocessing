import json
import os

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

    tokens_before = [t for t in tokens_before if len(t) > 0]
    tokens_after = [t for t in tokens_after if len(t) > 0]

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
            end_before = return_condition_extrema(tokens_before, l)  # find the end of the condition for before code
            end_after = return_condition_extrema(tokens_after, l)  # find the end of the condition for after code
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


'''
We check if all records are OK. Record that does not pass the check_record test are discarted
'''


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


'''
Remove all records whose length is greater than max_len
'''


def remove_longer_methods(max_len, input_file):
    path_remove_longer_methods = "data/miner_postprocessing/remove_longer_methods"

    if os.path.exists(path_remove_longer_methods) == False:
        os.makedirs(path_remove_longer_methods)

    files = os.listdir(path_remove_longer_methods)
    for f in files:
        os.remove(os.path.join(path_remove_longer_methods, f))

    # records_path = "data/miner_postprocessing/remove_wrong_records/result.txt"
    records_path = input_file
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


'''
Remove all duplicates
'''


def remove_duplicates(input_file):
    path_remove_duplicates = "data/miner_postprocessing/remove_duplicates"

    if os.path.exists(path_remove_duplicates) == False:
        os.makedirs(path_remove_duplicates)

    files = os.listdir(path_remove_duplicates)
    for f in files:
        os.remove(os.path.join(path_remove_duplicates, f))

    # records_path = "data/miner_postprocessing/remove_longer_methods/result.txt"
    records_path = input_file
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
'''
Export data file (id_internal, id_commit, repo, masked_code, before_code, after_code
'''