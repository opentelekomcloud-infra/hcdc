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


def encode_image_to_base64(image_path):
    # Open the image file in binary mode
    with open(image_path, "rb") as image_file:
        # Read the image data
        image_data = image_file.read()
        # Encode the image data to Base64
        base64_encoded_data = base64.b64encode(image_data)
        # Convert the Base64 bytes to a string
        base64_string = base64_encoded_data.decode('utf-8')
    return base64_string


def analyze_text(data):
    with open(data, 'r') as file:
        file_contents = file.read()
    
    if has_chinese(file_contents):
        return {
            "file": data, 
            "file_contents": file_contents
            "detected": True
        }

    else:
        return {
            "file": data, 
            "file_contents": file_contents
            "detected": False
        }

    

def process_textfiles(textfile_list, num_processes):
    with Pool(num_processes) as pool:
        results = pool.map(partial(analyze_text), textfile_list)
    return results


def has_chinese(text):
    # Regular expression to match Chinese characters
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    return bool(chinese_pattern.search(text))

def main(args):
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

    logging.debug(image_files)
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