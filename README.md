# github-org-repo-sync
Python script that syncs all repositories of a given GitHub Organization with your local machine


## Features

- Use the GitHub API to list all repositories of a given Organization name and clone it into the current directory (supports pagination)
- Supports GitHub and GitHub Enterprise
- Takes by default the current working directoy as organization name
- Provide the github token to fetch all repositories of the given org from a file or cli argument (defaults to `~/.github-token`)
- Optionally delete all folders in the current directory that are not a repository of the given organization

## Usage Example

```sh

python3 clone_all_repos_from_org.py 

python3 clone_all_repos_from_org.py -e --base-url git.company.com

python3 clone_all_repos_from_org.py -p ~/.secrets/my-github.token
```



## Help


```sh

~/repos/clone-all-repos-from-org.py --help
usage: clone-all-repos-from-org.py [-h] [-u BASE_URL] [-e] [-t TOKEN | -p TOKEN_FILE_PATH] [-o ORG_NAME] [-s] [-n] [-f]

This script is used to clone all repositories of a given GitHub organisation On top it cleans up the folders that are not part of that organization. You can adjust it using various parameters. For the organization name by default it will use the directory name of the
current working directory. For the token file by default it will use the token file located in the home directory named `~/.github-token`. Author: Dominik Bartsch

optional arguments:
  -h, --help            show this help message and exit
  -u BASE_URL, --base_url BASE_URL
                        The base URL for the GitHub Enterprise API (without http/ssl/git).
  -e, --enterprise-api  Defines if you want to call the GitHub Enterprise API.
  -t TOKEN, --token TOKEN
                        The authentication token to use for the API request.
  -p TOKEN_FILE_PATH, --token_file_path TOKEN_FILE_PATH
                        The path to the token file.
  -o ORG_NAME, --org_name ORG_NAME
                        The name of the GitHub organization to clone.
  -s, --ssl             If provided using ssh for cloning instead of https.
  -n, --no-delete-obsolete-folders
                        If provided the script won't delete folders that are not present in the github organization
  -f, --force-deletion  If provided the script will not ask to delete the folders that are not part of the organization.


```
