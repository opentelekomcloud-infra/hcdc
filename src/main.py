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
import argparse
import git
from src.image_processing import main as image_processing
from src.text_processing import main as text_processing
import json


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
        '--image-file-extensions',
        metavar='<file-extensions>',
        default=['.jpg', '.png', '.jpeg', '.gif', '.tiff', '.bmp'],
        nargs='+',
        help='Image file extensions which should be checked.'
             'Default: .jpg .png .jpeg .gif .webp .avif'
    )
    parser.add_argument(
        '--text-file-extensions',
        metavar='<file-extensions>',
        default=['.txt', '.md', '.rst', '.ini', '.cfg', '.json', '.xml', '.yml', '.yaml', '.py', '.html', '.htm'],
        nargs='+',
        help='Text file extensions which should be checked.'
             'Default: .txt .md .rst .ini .cfg. json .xml .yml .yaml .py'
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
        default="https://ocr.eu-de.otc.t-systems.com/v2/project-id/ocr/general-text",
        help='URL for OCR Service.'
             ' Default: https://ocr.eu-de.otc.t-systems.com/v2/project-id/ocr/general-text'
    )
    parser.add_argument(
        '--regex-pattern',
        metavar='<regex-pattern>',
        default=[r'(?![\u4e2a\u516b\u4e00\u4eba])[\u4e01-\u9fff]+'],
        nargs='+',
        help='Regex pattern to check for unwanted characters.'
             'Default: ' + (r'(?![\u4e2a\u516b\u4e00\u4eba])[\u4e01-\u9fff]+')
    )
    args = parser.parse_args()
    return args

def get_changed_files(repo_path, branch, main_branch):
    repo = git.Repo(repo_path)

    # Checkout the branch
    repo.git.checkout(branch)

    # Fetch the main branch to ensure we have the latest changes
    repo.remotes.origin.fetch(main_branch)

    # Get the diff between the main branch and the specified branch, only changed and new files
    diff = repo.git.diff(main_branch, branch, name_only=True, diff_filter='AM')
    
    # Split the output by lines
    changed_files = diff.splitlines()

    return changed_files

def main():

    args = get_parser()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    changed_files=get_changed_files(
        args.repo_path,
        args.branch,
        args.main_branch
    )
    
    output_images = image_processing (
        args=args,
        changed_files=changed_files
    )

    output_text = text_processing (
        args=args,
        changed_files=changed_files
    )

    return json.dumps({
        "images": output_images,
        "text": output_text
    })
