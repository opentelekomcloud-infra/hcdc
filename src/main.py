import logging
from multiprocessing import Pool
import shutil
import argparse
import git
import os
from dotenv import load_dotenv
import requests
from multiprocessing import Pool
from functools import partial
import base64
import json
import re


def get_parser():
    # Format the output of help
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '--debug',
        action='store_true',
        help=' Option enables Debug output.'
    )
    parser.add_argument(
        '--processes',
        metavar='<processes>',
        default=4,
        help='Number of processes for minification.'
             ' Default: 4'
    )
    parser.add_argument(
        '--repo-path',
        metavar='<repo-path>',
        default=".",
        help='Path to git repository.'
             ' Default: .'
    )
    parser.add_argument(
        '--file-extensions',
        metavar='<file-extensions>',
        default=['.jpg', '.png', '.jpeg', '.gif', '.tiff', '.bmp'],
        nargs='+',
        help='File extensions which should be checked.'
             ' Default: .jpg .png .jpeg .gif .webp .avif'
    )
    parser.add_argument(
        '--branch',
        metavar='<branch>',
        default="umn",
        help='Branch to compare against main branch.'
             ' Default: umn'
    )
    parser.add_argument(
        '--main-branch',
        metavar='<main-branch>',
        default="main",
        help='Name of the main branch.'
             ' Default: main'
    )
    parser.add_argument(
        '--ocr-url',
        metavar='<ocr-url>',
        default="https://ocr.eu-de.otc.t-systems.com/v2/16d53a84a13b49529d2e2c3646691288/ocr/general-text",
        help='URL for OCR Service.'
             ' Default: https://ocr.eu-de.otc.t-systems.com/v2/16d53a84a13b49529d2e2c3646691288/ocr/general-text'
    )
    args = parser.parse_args()
    return args


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


def main():

    args = get_parser()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    load_dotenv('.env')
    auth_token = os.getenv('AUTH_TOKEN')
    # logging.debug("Environment variables: %s", os.environ)
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

    # print(image_files)
    # print(json.dumps(results))

    # List to store image files with Chinese characters
    images_with_chinese = []

    # Iterate through OCR response
    for entry in results:
        words_blocks = entry["response"]["result"]["words_block_list"]
        for block in words_blocks:
            if has_chinese(block["words"]):
                images_with_chinese.append(entry["data"])
                break

    # Print the list of image files containing Chinese characters
    print("Image files containing Chinese characters:")
    print(images_with_chinese)
