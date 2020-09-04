#!/usr/bin/env python3

# YJK's ON-FLEEK PRE-COMMIT CI LINTER
# To use:
# Install python3
# pip install requests
# Set environment variable GITLAB_AUTH_TOKEN in your shell's rc file
# In <repository-root>/.git/hooks run:
# ln -s ../../ci_utils/ci_lint.py pre-commit
# chmod +x .git/hooks/pre-commit
import os
import sys

import requests

LINTER_URL = 'https://<your-gitlab-repo>/api/v4/ci/lint'


def lint(token, ci_yml):
    with open(ci_yml) as f:
        r = requests.post(LINTER_URL,
                          params={
                              'private_token': token,
                          },
                          headers={
                              'Content-Type': 'application/json',
                          },
                          json={'content': f.read()})

    print(f'status code: {r.status_code}')
    if r.status_code != requests.codes.ALL_OK:
        print(f'BAD REQUEST: {r.status_code}')
        sys.exit(1)

    data = r.json()
    if data['status'] != 'valid':
        for e in data['errors']:
            print(e, file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    ci_yml = '.gitlab-ci.yml'
    token = os.getenv('GITLAB_AUTH_TOKEN')
    if not token:
        print('Please set GITLAB_AUTH_TOKEN environment variable')
        sys.exit(1)

    cmd = "git diff-index --name-only --diff-filter M HEAD | grep '^.gitlab-ci.yml$'"
    ci_changed = os.system(cmd) == 0
    if ci_changed:
      lint(token, ci_yml)
