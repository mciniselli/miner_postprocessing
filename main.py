import json
import os
import sys

from utils.input_output import write_file
from utils.utilities import *

from utils.check_record import *


import numpy as np
from utils.original_code_integration import *
import requests

from utils.export_file import *
from utils.original_code_integration import *

from utils.data_analysis import *


def main():
    print("start mining")

    files = getListOfFiles("data/condition_bugfix")

    java_files = [f for f in files if f.endswith(".txt")]
    print(java_files)

    output = ""

    # output=remove_wrong_records(java_files)
    # output=remove_longer_methods(150, output)
    #
    # output=remove_duplicates(output)
    #
    # add_original_code("data/miner_postprocessing/remove_duplicates/result.txt")
    #
    # export_files_masked("data/miner_postprocessing/add_original_code/result.txt")
    #
    # inspect_data()

    count_occurrences("/home/matteoc/dataset_creation_3_chunks/")
    # count_occurrences("result")

    get_global_results()


if __name__ == "__main__":
    main()
