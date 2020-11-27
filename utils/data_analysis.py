
import os

from utils.input_output import read_file, write_file


'''
Print a result file to check the changes between before and after
'''


def inspect_data():
    save_folder = "data/miner_postprocessing/inspect_data"

    if os.path.exists(save_folder) == False:
        os.makedirs(save_folder)

    files = os.listdir(save_folder)
    for f in files:
        os.remove(os.path.join(save_folder, f))

    save_file = "data/miner_postprocessing/inspect_data/result.txt"

    input_folder = "data/miner_postprocessing/export_files_masked"

    masked_code = read_file(os.path.join(input_folder, "masked_code.txt"))
    mask_before = read_file(os.path.join(input_folder, "mask_before.txt"))
    mask_after = read_file(os.path.join(input_folder, "mask_after.txt"))

    result = list()

    for x, y, z in zip(masked_code, mask_before, mask_after):
        result.append("----------")
        masked_parts = x.split("<x>")
        result.append(masked_parts[0])
        result.append("-- " + y.replace("<z>", ""))
        result.append("++ " + z.replace("<z>", ""))
        result.append(masked_parts[1])

    write_file(save_file, result)


def count_occurrences(base_path):
    subdirs = [x[0] for x in os.walk(base_path)]

    for s in subdirs:

        num_for = 0
        num_if = 0
        num_while = 0

        len_method = list()
        len_masked = list()

        num_less_150 = 0

        num_for_ok = 0
        num_if_ok = 0
        num_while_ok = 0

        len_method_ok = list()
        len_masked_ok = list()

        num_less_150_ok = 0

        if "result" in s:
            method_file = os.path.join(s, "methods.txt")
            masked_method_file = os.path.join(s, "masked_methods.txt")
            methods = read_file(method_file)
            masked_methods = read_file(masked_method_file)

            for masked_method in masked_methods:

                masked_method_splitted = masked_method.split("|_|")

                method_id = int(masked_method_splitted[1])

                method = methods[method_id - 1]

                type = masked_method_splitted[6]
                if type == "IF":
                    num_if += 1
                elif type == "FOR":
                    num_for += 1
                else:
                    num_while += 1

                method_token = eval((method.split("|_|"))[1])

                num_tokens = 0
                for t in method_token:
                    if t != " ":
                        num_tokens += 1

                if num_tokens <= 150:
                    num_less_150 += 1

                len_method.append(num_tokens)
                start_masked = int(masked_method_splitted[4])
                end_masked = int(masked_method_splitted[5])

                tokens_condiion = method_token[start_masked:end_masked]
                num_tokens_condition = 0
                for t in tokens_condiion:
                    if t != " ":
                        num_tokens_condition += 1

                len_masked.append(num_tokens_condition)

                condition = "".join(tokens_condiion)
                condition = condition.replace(" ", "")

                if "&&" in condition or "||" in condition:
                    continue

                if "!=null" in condition or "==null" in condition:
                    if type == "IF":
                        num_if_ok += 1
                    elif type == "FOR":
                        num_for_ok += 1
                    else:
                        num_while_ok += 1

                    if num_tokens <= 150:
                        num_less_150_ok += 1

                    len_method_ok.append(num_tokens)
                    len_masked_ok.append(num_tokens_condition)

            res = list()
            res.append("GLOBAL")
            res.append("NUM IF {}, FOR {}, WHILE {} OUT OF {}".format(num_if, num_for, num_while, len(len_masked)))
            res.append("MEAN LEN METHOD {}, VARIANCE {}".format(np.mean(len_method), np.var(len_method)))
            res.append("MEAN LEN MASKED {}, VARIANCE {}".format(np.mean(len_masked), np.var(len_masked)))
            res.append("{} METHOD WHOSE LENGTH < 150".format(num_less_150))

            res.append("OK VALUES")
            res.append(
                "NUM IF {}, FOR {}, WHILE {} OUT OF {}".format(num_if_ok, num_for_ok, num_while_ok, len(len_masked_ok)))
            res.append("MEAN LEN METHOD {}, VARIANCE {}".format(np.mean(len_method_ok), np.var(len_method_ok)))
            res.append("MEAN LEN MASKED {}, VARIANCE {}".format(np.mean(len_masked_ok), np.var(len_masked_ok)))
            res.append("{} METHOD WHOSE LENGTH < 150".format(num_less_150_ok))

            write_file("analysis results_{}.txt".format(s.replace("/", "_")), res)


def get_global_results():
    save_folder = "data/miner_postprocessing/count_occurrences"
    files = os.listdir(save_folder)
    files = [f for f in files if "results" in f]

    num_for = 0
    num_if = 0
    num_while = 0

    method_len = 0
    method_var = 0

    masked_len = 0
    masked_var = 0

    num_masked = 0
    num_less_150 = 0

    num_less_150 = 0

    num_for_ok = 0
    num_if_ok = 0
    num_while_ok = 0

    method_len_ok = 0
    method_var_ok = 0

    masked_len_ok = 0
    masked_var_ok = 0

    num_masked_ok = 0
    num_less_150_ok = 0

    for f in files:
        lines = read_file(os.path.join(save_folder, f))
        lines = [l.replace(",", "") for l in lines]

        count_line = lines[1]
        r = [int(s) for s in count_line.split() if s.isdigit()]
        num_if += r[0]
        num_for += r[1]
        num_while += r[2]
        num_masked += r[3]
        num_curr = float(r[3])

        count_line = lines[2]
        r = count_line.split(" ")
        mean = float(r[3])
        variance = float(r[5])
        method_len += (num_curr * mean)
        method_var += (num_curr * variance)

        count_line = lines[3]
        r = count_line.split(" ")
        mean = float(r[3])
        variance = float(r[5])
        masked_len += (num_curr * mean)
        masked_var += (num_curr * variance)

        count_line = lines[4]
        r = count_line.split(" ")
        num = int(r[0])
        num_less_150 += num

        count_line = lines[6]
        r = [int(s) for s in count_line.split() if s.isdigit()]
        num_if_ok += r[0]
        num_for_ok += r[1]
        num_while_ok += r[2]
        num_masked_ok += r[3]
        num_curr = float(r[3])

        count_line = lines[7]
        r = count_line.split(" ")
        mean = float(r[3])
        variance = float(r[5])
        method_len_ok += (num_curr * mean)
        method_var_ok += (num_curr * variance)

        count_line = lines[8]
        r = count_line.split(" ")
        mean = float(r[3])
        variance = float(r[5])
        masked_len_ok += (num_curr * mean)
        masked_var_ok += (num_curr * variance)

        count_line = lines[9]
        r = count_line.split(" ")
        num = int(r[0])
        num_less_150_ok += num

    res = list()
    res.append("GLOBAL")
    res.append("NUM IF {}, FOR {}, WHILE {} OUT OF {}".format(num_if, num_for, num_while, num_masked))
    res.append("MEAN LEN METHOD {}, VARIANCE {}".format(method_len / num_masked, method_var / num_masked))
    res.append("MEAN LEN MASKED {}, VARIANCE {}".format(masked_len / num_masked, masked_var / num_masked))
    res.append("{} METHOD WHOSE LENGTH < 150".format(num_less_150))
    res.append("OK VALUES")
    res.append("NUM IF {}, FOR {}, WHILE {} OUT OF {}".format(num_if_ok, num_for_ok, num_while_ok, num_masked_ok))
    res.append("MEAN LEN METHOD {}, VARIANCE {}".format(method_len_ok / num_masked_ok, method_var_ok / num_masked_ok))
    res.append("MEAN LEN MASKED {}, VARIANCE {}".format(masked_len_ok / num_masked_ok, masked_var_ok / num_masked_ok))
    res.append("{} METHOD WHOSE LENGTH < 150".format(num_less_150_ok))

    write_file(os.path.join(save_folder, "FINAL.txt"), res)