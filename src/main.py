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
from image_processing import main as image_processing


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
        default="https://ocr.eu-de.otc.t-systems.com/v2/project-id/ocr/general-text",
        help='URL for OCR Service.'
             ' Default: https://ocr.eu-de.otc.t-systems.com/v2/project-id/ocr/general-text'
    )
    args = parser.parse_args()
    return args

def main():

    args = get_parser()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    json_output = image_processing(args)

    return json_output
