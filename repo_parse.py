#!/usr/bin/env python3
from collections import namedtuple
from urllib.parse import urlparse
import os.path
import sys


ParsedUrl = namedtuple("ParsedUrl", ["repo_url", "branch", "file_path"])


def parse_url(url_str):
    url = urlparse(url_str)
    paths = list(filter(bool, url.path.split("/")))
    netloc = url

    if url.netloc in ["github.com", "raw.githubusercontent.com"]:
        repo_host = "git@github.com"
    elif url.netloc in ["gitlab.com"]:
        repo_host = "git@gitlab.com"
    else:
        raise ValueError("Unknown git host: {}".format(url.netloc))

    # GitHub and GitLab mostly share naming schema
    repo_owner, repo_name = paths[0:2]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]
    repo_url = "{}:{}/{}.git".format(repo_host, repo_owner, repo_name)
    if len(paths) == 2:
        return ParsedUrl(repo_url=repo_url, branch=None, file_path="")

    if url.netloc in ["raw.githubusercontent.com"]:
        branch = paths[2]
        file_path = os.path.join(".", *paths[3:])
    else:
        if url.netloc == "github.com":
            assert paths[2] in ["tree", "blob"]
        elif url.netloc ==  "gitlab.com":
            assert paths[2] in ["tree", "blob", "raw"]
        else:
            assert False
        branch = paths[3]
        file_path = os.path.join(".", *paths[4:])

    return ParsedUrl(repo_url=repo_url, branch=branch, file_path=file_path)


def main():
    assert len(sys.argv[1])
    parsed_url = parse_url(sys.argv[1])
    result = "{0.repo_url} {0.branch} {0.file_path}".format(parsed_url)
    assert result.count(" ") == 2
    print(result)


if __name__ == "__main__":
    main()
