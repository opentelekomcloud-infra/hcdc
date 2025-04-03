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

import base64
import json
import logging
import os
import re
import sys
from functools import partial
from multiprocessing import Pool

import requests
from dotenv import load_dotenv


def get_changed_image_files(changed_files, file_extensions):
    # Filter files by the given extensions
    image_files = [
        file
        for file in changed_files
        if any(file.endswith(ext) for ext in file_extensions)
    ]
    return image_files


def encode_image_to_base64(image_path):
    try:
        # Open the image file in binary mode
        with open(image_path, "rb") as image_file:
            # Read the image data
            image_data = image_file.read()
            # Encode the image data to Base64
            base64_encoded_data = base64.b64encode(image_data)
            # Convert the Base64 bytes to a string
            base64_string = base64_encoded_data.decode("utf-8")
        return base64_string
    except Exception as e:
        logging.error(f"Failed to analyze image {image_path}: {e}")
        return "Error"


def post_request(data, url, headers):
    try:
        image_base64 = encode_image_to_base64(data)
        if image_base64 == "Error":
            return {"data": data, "status": "failure"}
        final_json = {
            "image": image_base64,
            "detect_direction": False,
            "quick_mode": False,
        }
        response = requests.post(url, json=final_json, headers=headers)
        if response.status_code == 200:
            return {
                "data": data,
                "status": "success",
                "response": response.json(),
            }
        else:
            return {
                "data": data,
                "status": "failure",
                "status_code": response.status_code,
                "response": response.text,
            }
    except requests.exceptions.RequestException as e:
        return {"data": data, "status": "error", "error": str(e)}


def process_images(image_list, url, num_processes, headers):
    num_processes = int(num_processes)
    with Pool(num_processes) as pool:
        results = pool.map(
            partial(post_request, url=url, headers=headers), image_list
        )
    return results


def detect_chars(text, regex_pattern):
    try:
        for pattern in regex_pattern:
            char_pattern = re.compile(pattern)
            match = char_pattern.search(text)
            if match:
                return {"detected": True, "char": match.group(0)}
            else:
                return {"detected": False, "char": None}

    except Exception as e:
        logging.error(f"Invalid regex pattern: {e}")
        sys.exit(1)


def main(args, changed_files):
    load_dotenv(".env")
    auth_token = os.getenv("AUTH_TOKEN")
    if not auth_token:
        raise ValueError(
            "Wrong or not specified value for AUTH_TOKEN environment variable!"
        )

    file_extensions = args.image_file_extensions
    num_processes = args.processes
    ocr_url = args.ocr_url
    regex_pattern = args.regex_pattern
    min_char_count = args.min_char_count

    logging.info("Starting to analyze changed images...")

    image_files = get_changed_image_files(
        changed_files=changed_files, file_extensions=file_extensions
    )

    logging.info("Changed images:" + str(image_files))

    headers = {"X-Auth-Token": auth_token, "Content-Type": "application/json"}

    results = process_images(
        image_list=image_files,
        url=ocr_url,
        num_processes=num_processes,
        headers=headers,
    )

    logging.debug(image_files)
    logging.debug(json.dumps(results))

    images_with_chinese = []
    for entry in results:
        if entry["status"] == "failure":
            continue

        words_blocks = entry["response"]["result"]["words_block_list"]
        detected_character_list = []
        detect_status = False

        for block in words_blocks:
            chinese_result = detect_chars(
                block["words"], regex_pattern=regex_pattern
            )

            if chinese_result["detected"]:
                confidence = block["confidence"]
                detected_chars = chinese_result["char"]
                file_name = entry["data"]

                if confidence < float(args.confidence):
                    warning_msg = (
                        f"Detected Chinese character {detected_chars} "
                        f"in file {file_name} "
                        f"with low confidence of {confidence}."
                    )
                    logging.warning(warning_msg)
                else:
                    if len(detected_chars) >= int(min_char_count):
                        detect_status = True
                        detected_character_list.append(
                            {"text": detected_chars, "confidence": confidence}
                        )
        if detect_status is True:
            images_with_chinese.append(
                {
                    "file": file_name,
                    "matches": detected_character_list,
                    "detected": True,
                    "status": entry["status"],
                }
            )

    if images_with_chinese == []:
        detect_dict = {"detected": False, "files": images_with_chinese}
    else:
        detect_dict = {"detected": True, "files": images_with_chinese}

    return detect_dict
