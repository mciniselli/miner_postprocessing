import json
import os

from utils.input_output import write_file

'''
given the list of tokens and the index of the first token that is different in before and after code, it returns the start and the end token of the if/for or while condition before that position
'''


def export_files_masked(input_file):
    path_export_files_masked = "data/miner_postprocessing/export_files_masked"

    if os.path.exists(path_export_files_masked) == False:
        os.makedirs(path_export_files_masked)

    files = os.listdir(path_export_files_masked)
    for f in files:
        os.remove(os.path.join(path_export_files_masked, f))

    # records_path = "data/miner_postprocessing/remove_duplicates/result.txt"
    records_path = input_file

    fields_to_export = ["id_internal", "id_commit", "repo"]

    for field in fields_to_export:
        list_to_export = list()
        with open(records_path) as f:
            for line in f:
                data = json.loads(line)
                list_to_export.append(data[field])

        write_file(os.path.join(path_export_files_masked, "{}.txt".format(field)), list_to_export)

    list_masked_code = list()
    list_mask_before = list()
    list_mask_after = list()

    with open(records_path) as f:
        for line in f:
            data = json.loads(line)
            before_code = eval(data["before"])
            before_index = data["mask_before_index"].split(" ")
            start_before = int(before_index[0])
            end_before = int(before_index[1])

            after_code = eval(data["after"])
            after_index = data["mask_after_index"].split(" ")
            start_after = int(after_index[0])
            end_after = int(after_index[1])
            # masked_before=" ".join(before_code[:start_before+1])+" <x>" + " ".join(before_code[end_before+1:])
            # masked_after=" ".join(after_code[:start_after+1])+" <x>" + " ".join(after_code[end_after+1:])

            masked_bef_1, index_bef_1 = return_code(before_code[:start_before + 1], data["before_code"], False)
            masked_bef_2, index_bef_2 = return_code(before_code[end_before + 1:], data["before_code"], True)

            masked_before = masked_bef_1 + " <x>" + masked_bef_2

            masked_aft_1, index_aft_1 = return_code(after_code[:start_after + 1], data["after_code"], False)
            masked_aft_2, index_aft_2 = return_code(after_code[end_after + 1:], data["after_code"], True)

            masked_after = masked_aft_1 + " <x>" + masked_aft_2

            if masked_before != masked_after:  # it should not happen (only some cases when the developer changed the spaces out of the if while or loop)
                print("ERROR")

            # mask_before=" ".join(before_code[start_before+1:end_before+1]) + "<z>"
            # mask_after=" ".join(after_code[start_after+1:end_after+1]) + "<z>"
            mask_before = data["before_code"][index_bef_1:index_bef_2] + "<z>"
            mask_after = data["after_code"][index_aft_1:index_aft_2] + "<z>"

            # mask_before= return_code(before_code[start_before+1::end_before+1], data["before_code"], False)+ "<z>"
            # mask_after= return_code(after_code[start_after+1::end_after+1], data["after_code"], False)+ "<z>"

            list_masked_code.append(masked_before)
            list_mask_before.append(mask_before)
            list_mask_after.append(mask_after)

    write_file(os.path.join(path_export_files_masked, "{}.txt".format("masked_code")), list_masked_code)
    write_file(os.path.join(path_export_files_masked, "{}.txt".format("mask_before")), list_mask_before)
    write_file(os.path.join(path_export_files_masked, "{}.txt".format("mask_after")), list_mask_after)


'''
return the source code from the whole file
'''


def return_code(tokens, text, reverse):
    if reverse == False:

        text_new = text
        for t in tokens:
            text_new = text_new.replace(t, " " * (len(t)), 1)

        for i, t in enumerate(text_new):
            if t != " ":
                return text[:i].strip(), i
    else:

        text_new = text[::-1]
        for t in tokens[::-1]:
            text_new = text_new.replace(t[::-1], " " * (len(t)), 1)

        for i, t in enumerate(text_new):
            if t != " ":
                return text[::-1][:i][::-1].strip(), len(text) - i

