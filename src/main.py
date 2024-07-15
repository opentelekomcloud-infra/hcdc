import logging
from multiprocessing import Pool
import shutil
import argparse
import git
import os
from dotenv import load_dotenv


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
        default=['.jpg', '.png', '.jpeg', '.gif', '.webp', '.avif'],
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
    args = parser.parse_args()
    return args


def get_changed_image_files(repo_path, branch, main_branch, file_extensions):
    """
    Get a list of changed files in the given branch compared to another branch.

    :param repo_path: Path to the git repository.
    :param main_branch: Name of the main branch.
    :param branch: Name of the branch to compare.
    :param file_extensions: List of file extensions to filter (e.g., ['.png', '.jpg']).
    :return: List of changed image files.
    """
    repo = git.Repo(repo_path)

    # Fetch the main branch to ensure we have the latest changes
    repo.remotes.origin.fetch(main_branch)

    # Get the diff between the main branch and the specified branch
    diff = repo.git.diff(main_branch, branch, name_only=True)
    
    # Split the output by lines
    changed_files = diff.splitlines()

    # Filter files by the given extensions
    image_files = [file for file in changed_files if any(file.endswith(ext) for ext in file_extensions)]

    return image_files



def main():

    args = get_parser()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    load_dotenv()
    auth_token = os.getenv('AUTH_TOKEN')
    logging.debug("Environment variables: %s", os.environ)
    if auth_token == '' or auth_token is None:
        raise ValueError("Wrong or not specified value for AUTH_TOKEN environment variable!")
    
    print(auth_token)

    main_branch = args.main_branch
    branch = args.branch
    repo_path = args.repo_path
    file_extensions = args.file_extensions

    logging.info("Starting to analyze changed images...")

    image_files = get_changed_image_files(
        repo_path=repo_path,
        branch=branch,
        main_branch=main_branch,
        file_extensions=file_extensions
    )

    print(image_files)
