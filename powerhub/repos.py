import subprocess
import os
import urllib.request
from urllib.parse import urlparse
from powerhub.upload import BASE_DIR

module_dir = os.path.join(BASE_DIR, "modules")

repositories = {
    "AdrianVollmer/PowerSploit": "https://github.com/AdrianVollmer/PowerSploit.git",
    "BloodHound": "https://github.com/BloodHoundAD/BloodHound.git",
    "ASREPRoast": "https://github.com/HarmJ0y/ASREPRoast.git",
}


def install_repo(repo, custom_repo=None):
    """Download a repository; custom repositories have precedence"""
    if custom_repo:
        return install_repo_from_url(custom_repo)
    else:
        return install_repo_from_url(repositories[repo])


def install_repo_from_url(url):
    """Determine the type of a module and install it accordingly"""
    parsed_url = urlparse(url)
    basename = os.path.basename(parsed_url.path)
    if basename.endswith('.git'):
        return git_clone(url)
    elif basename.endswith('.ps1') or basename.endswith('.exe'):
        return download(url)
    else:
        return f"Unknown extension: {url}", "danger"


def git_clone(url):
    """Installs a git repository"""
    parsed_url = urlparse(url)
    basename = os.path.basename(parsed_url.path)
    dest_dir = os.path.join(module_dir, 'ps1', basename[:-4])
    if os.path.isdir(dest_dir):
        return f"Directory already exists: {dest_dir}", "danger"
    try:
        subprocess.check_output(['git', 'clone', '--depth', '1',
                                 url, dest_dir],
                                stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return f"Error while cloning '{url}': {e.output.decode()}", "danger"
    return f"Successfully cloned git repository: {url}", "success"


def download(url):
    """Downloads a module that is not a git repository"""
    parsed_url = urlparse(url)
    basename = os.path.basename(parsed_url.path)
    extension = basename[-3:]
    try:
        response = urllib.request.urlopen(url)
        data = response.read()
    except Exception as e:
        return f"Error while accessing URL: {str(e)}", "danger"
    filename = os.path.join(module_dir, extension, basename)
    if os.path.isfile(filename):
        return f"File already exists: {filename}", "danger"
    with open(filename, 'wb') as f:
        f.write(data)
    return f"Successfully downloaded file: {url}", "success"
