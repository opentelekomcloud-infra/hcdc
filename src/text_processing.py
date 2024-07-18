# Copyright 2024 Open Telekom Cloud Ecosystem Squad

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from multiprocessing import Pool
import shutil
import git
import os
from dotenv import load_dotenv
from functools import partial
import base64
import json
import re


def get_changed_text_files(changed_files, file_extensions):
    # Filter files by the given extensions
    text_files = [file for file in changed_files if any(file.endswith(ext) for ext in file_extensions)]

    return text_files


def analyze_text(data):
    try:
        with open(data, 'r') as file:
            file_contents = file.read()
        
        if has_chinese(file_contents):
            return {
                "file": data, 
                "file_contents": file_contents,
                "detected": True,
                "status": "success"
            }

        else:
            return {
                "file": data, 
                "file_contents": file_contents,
                "detected": False,
                "status": "success"
            }
    except Exception as e:
        logging.error(f"Failed to analyze textfile {data}: {e}")
        return {
                "file": data, 
                "status": "failure"
            }

    

def process_textfiles(textfile_list, num_processes):
    with Pool(num_processes) as pool:
        results = pool.map(partial(analyze_text), textfile_list)
    return results


def has_chinese(text):
    # Regular expression to match Chinese characters
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    return bool(chinese_pattern.search(text))

def main(args, changed_files):
    file_extensions = args.text_file_extensions
    num_processes = args.processes

    logging.info("Starting to analyze changed textfiles...")

    textfile_list = get_changed_text_files(
        changed_files=changed_files,
        file_extensions=file_extensions
    )

    results = process_textfiles(
        textfile_list=textfile_list,
        num_processes=num_processes,
    )

    logging.debug(textfile_list)
    logging.debug(json.dumps(results))

    text_with_chinese = []
    for entry in results:
        if entry["detected"] is True:
            text_with_chinese.append(entry)

    if text_with_chinese == []:
        detect_dict = {
            "detected": False,
            "files": text_with_chinese
        }
    else:
        detect_dict = {
            "detected": True,
            "files": text_with_chinese
        }
    
    return detect_dict