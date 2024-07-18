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

# The provided script analyzes text files to detect the presence of
# Chinese characters and processes them using multiprocessing.

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
    text_files = [file for file in changed_files if os.path.splitext(file)[1] in file_extensions]
    return text_files

def analyze_text(data):
    try:
        with open(data, 'r') as file:
            file_contents = file.read()
        
        result = has_chinese(file_contents)

        if result["detected"]:
            return {
                "file": data, 
                "matches": result["matches"],
                "detected": True,
                "status": "success"
            }
        else:
            return {
                "file": data, 
                "matches": [],
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
    num_processes = max(1, int(num_processes))
    with Pool(num_processes) as pool:
        results = pool.map(analyze_text, textfile_list)
    return results

def has_chinese(text):
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    res = {
        "detected": False,
        "matches": []
    }
    
    lines = text.splitlines()
    for line_num, line in enumerate(lines, 1):
        for match in chinese_pattern.finditer(line):
            match_info = {
                "text": match.group(),
                "line": line_num,
                "start_position": match.start() + 1,  # +1 to convert to 1-based index
                "end_position": match.end()  # end position as 1-based index
            }
            res["matches"].append(match_info)
    
    if res["matches"]:
        res["detected"] = True
    
    return res

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

    text_with_chinese = [entry for entry in results if entry.get("detected")]

    detect_dict = {
        "detected": bool(text_with_chinese),
        "files": text_with_chinese
    }
    
    return detect_dict
