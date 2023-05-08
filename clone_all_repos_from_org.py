#!/usr/bin/env python3

import requests
import subprocess
import argparse
import os
import shutil


help_text = """
This script is used to clone all repositories of a given GitHub organisation
On top it cleans up the folders that are not part of that organization.

You can adjust it using various parameters.
For the organization name by default it will use the directory name of the current working directory.
For the token file by default it will use the token file located in the home directory named `~/.github-token`.

Author: Dominik Bartsch
"""


def _read_token() -> str:
    """
    Read the token from the token file or from the arguments if provided.

    :return: token
    """

    with open(os.path.expanduser(args.token_file_path)) as f:
        return f.readline().strip()


def _get_current_folder_name():
    """
    Get the name of the current folder.

    :return: the name of the current folder
    """

    current_folder = os.getcwd()
    current_folder_name = os.path.basename(current_folder)
    return current_folder_name


def cleanup_folder_diff(all_repo_names):
    """
    Delete the folders that are not in the organization.
    """

    # find the diff between the folders in the current folder and the repos of the org
    existing_folders = [name for name in os.listdir(
        ".") if os.path.isdir(os.path.join(".", name))]
    diff = list(set(existing_folders) - set(all_repo_names))

    # ask for confirmation
    if len(diff) > 0:
        print(f"The following folders are not in the organization:")
        for repo in diff:
            print(repo)
        if not args.force_deletion:
            answer = input("Do you want to continue? [Y/n] ")
            if answer.lower() == "n":
                return
    else:
        print("Did not find any folders that are not in the organization.")
        return

    print("Deleting the folders...")
    for folder in diff:
        path_to_delete = os.path.join(".", folder)
        shutil.rmtree(path_to_delete)


def clone_all_repos(repository_names):
    """
    Clone all the repositories in the organization.

    :param repository_names: list of repository names
    """

    # if ssl argument provided then use git and ssh keys
    if args.ssl:
        api_url = f"git@{args.base_url}:{org_name}"
    else:
        api_url = f"https://{args.base_url}/{org_name}"

    for repo_name in repository_names:
        repo_url = f"{api_url}/{repo_name}"
        subprocess.call(
            f"git clone {repo_url}", shell=True)


def extract_repository_list(repositories_json: dict) -> list:
    """
    Extract the repository names from the repositories json.

    :param repositories_json: json of repositories provided by the GitHub API
    :return: list of repository names
    """

    all_repo_names = []
    for repo in repositories_json:
        all_repo_names.append(repo["name"])
    return all_repo_names


def get_repository_details():
    """
    Get the details of all the repositories in the organization.

    :return: yielding list of repositories, each call returns the next page
    """

    if args.enterprise_api:
        api_url = f"https://{args.base_url}/api/v3/orgs/{org_name}/repos"
    else:
        # using public github api url
        api_url = f"https://api.{args.base_url}/orgs/{org_name}/repos"
    token = args.token if args.token else _read_token()

    headers = {
        "Authorization": "Bearer " + token
    }

    session = requests.Session()

    response = session.get(api_url, headers=headers)
    if response.status_code == 200:
        yield response.json()
        next_page = response

        while next_page.links.get("next", None):
            next_url = next_page.links["next"]["url"]
            next_page = session.get(next_url, headers=headers)
            yield next_page.json()

    else:
        print(response.status_code)
        print(response.text)
        exit(1)


def get_org_name():
    """
    Get the name of the GitHub organization.

    :return: the name of the organization
    """

    return args.org_name if args.org_name else _get_current_folder_name()


if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description=help_text,
        add_help=True
    )
    parser.add_argument(
        "-u",
        "--base_url",
        help="The base URL for the GitHub Enterprise API (without http/ssl/git).",
        default="github.com"
    )
    parser.add_argument(
        "-e",
        "--enterprise-api",
        help="Defines if you want to call the GitHub Enterprise API.",
        action="store_true"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-t",
        "--token",
        help="The authentication token to use for the API request."
    )
    group.add_argument(
        "-p",
        "--token_file_path",
        help="The path to the token file.",
        default="~/.github-token"
    )
    parser.add_argument(
        "-o",
        "--org_name",
        help="The name of the GitHub organization to clone."
    )
    parser.add_argument(
        "-s",
        "--ssl",
        help="If provided using ssh for cloning instead of https.",
        action="store_true"
    )
    parser.add_argument(
        "-n",
        "--no-delete-obsolete-folders",
        help="If provided the script won't delete folders that are not present in the github organization",
        action="store_true"
    )
    parser.add_argument(
        "-f",
        "--force-deletion",
        help="If provided the script will not ask to delete the folders that are not part of the organization.",
        action="store_true"
    )
    args = parser.parse_args()

    org_name = get_org_name()

    all_repos = []
    for repository_page in get_repository_details():
        all_repos += extract_repository_list(repository_page)
        print(f"Parsed {len(all_repos)} repos")

    print("Cloning all repositories...")
    clone_all_repos(all_repos)

    if not args.no_delete_obsolete_folders:
        cleanup_folder_diff(all_repos)

    print("Done.")
    print("--------------------------------")
    print("Thanks for using the GitHub Sync Organization Repository Tool! 🎉")
    print("--------------------------------")
    exit(0)
