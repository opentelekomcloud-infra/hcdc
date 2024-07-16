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
import requests
from functools import partial
import base64
import json
import re


def get_changed_image_files(repo_path, branch, main_branch, file_extensions):
    repo = git.Repo(repo_path)

    # Checkout the branch
    repo.git.checkout(branch)

    # Fetch the main branch to ensure we have the latest changes
    repo.remotes.origin.fetch(main_branch)

    # Get the diff between the main branch and the specified branch
    diff = repo.git.diff(main_branch, branch, name_only=True)
    
    # Split the output by lines
    changed_files = diff.splitlines()

    # Filter files by the given extensions
    image_files = [file for file in changed_files if any(file.endswith(ext) for ext in file_extensions)]

    return image_files


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


def post_request(data, url, headers):
    try:
        image_base64 = encode_image_to_base64(data)
        final_json = {
            "image":image_base64,
            "detect_direction":False,
            "quick_mode":False
        }
        response = requests.post(url, json=final_json, headers=headers)
        if response.status_code == 200:
            return {"data": data, "status": "success", "response": response.json()}
        else:
            return {"data": data, "status": "failure", "status_code": response.status_code, "response": response.text}
    except requests.exceptions.RequestException as e:
        return {"data": data, "status": "error", "error": str(e)}

def process_images(image_list, url, num_processes, headers):
    with Pool(num_processes) as pool:
        results = pool.map(partial(post_request, url=url, headers=headers), image_list)
    return results


def has_chinese(text):
    # Regular expression to match Chinese characters
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    return bool(chinese_pattern.search(text))

def main(args):
    load_dotenv('.env')
    auth_token = os.getenv('AUTH_TOKEN')
    if auth_token == '' or auth_token is None:
        raise ValueError("Wrong or not specified value for AUTH_TOKEN environment variable!")

    main_branch = args.main_branch
    branch = args.branch
    repo_path = args.repo_path
    file_extensions = args.file_extensions
    num_processes = args.processes
    ocr_url = args.ocr_url

    logging.info("Starting to analyze changed images...")

    image_files = get_changed_image_files(
        repo_path=repo_path,
        branch=branch,
        main_branch=main_branch,
        file_extensions=file_extensions
    )

    headers = {
        "X-Auth-Token": auth_token,
        "Content-Type": "application/json"
    }

    results = process_images(
        image_list=image_files,
        url=ocr_url,
        num_processes=num_processes,
        headers=headers
    )

    logging.debug(image_files)
    logging.debug(json.dumps(results))

    images_with_chinese = []
    for entry in results:
        words_blocks = entry["response"]["result"]["words_block_list"]
        for block in words_blocks:
            if has_chinese(block["words"]):
                images_with_chinese.append(entry["data"])
                break

    if images_with_chinese == []:
        detect_dict = {
            "detected": False,
            "files": images_with_chinese
        }
    else:
        detect_dict = {
            "detected": True,
            "files": images_with_chinese
        }
    
    return json.dumps(detect_dict)