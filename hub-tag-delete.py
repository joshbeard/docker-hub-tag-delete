#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A script for cleaning up deprecated image tags on Docker Hub

This script parses a list of tags with deletion dates from a source document
and deletes them from the Docker Hub if they are present and the current date
has passed the specified deletion date.

The source for listing tags and their deletion dates can be a JSON file and/or
Markdown document. The Markdown source parses a table within specified
comment tags.

The source tag list supports wildcards. For example, '1.*' would match anything
beginning with '1.'. Refer to Python's 'fnmatch' module for more information
on wildcards: https://docs.python.org/3/library/fnmatch.html

Configuration is set using environment variables.

* Refer to the README.md file in this project's root directory for usage
  information.

* Refer to the LICENSE file in this project's root for license information.

Todo:
    * Pagination on Docker Hub results
    * Improve output (show scheduled date)
    * Support GitLab registry
    * CLI arguments

"""

import os
import http.client
import json
import fnmatch
from datetime import datetime

config = {
    'date_format': os.environ.get('DATE_FORMAT', '%B %d, %Y'),
    'docker_hub': {
        'api_host': os.environ.get('DOCKERHUB_API_HOST', 'hub.docker.com'),
        'username': os.environ.get('DOCKERHUB_USERNAME'),
        'password': os.environ.get('DOCKERHUB_PASSWORD')
    },
    'json': {
        'file': os.environ.get('JSON_FILE', None)
    },
    'markdown': {
        'file': os.environ.get('MARKDOWN_FILE', None),
        'format': 'table', # only 'table' is available currently.
        'begin_string': os.environ.get('MARKDOWN_BEGIN_STRING',
                                       '<!-- BEGIN deletion_table -->'),
        'end_string': os.environ.get('MARKDOWN_END_STRING',
                                     '<!-- END deletion_table -->')
    }
}

org, repo = os.environ.get('DOCKERHUB_REPOSITORY').split('/')
config['docker_hub']['organization'] = org
config['docker_hub']['repository'] = repo

now = datetime.now()


def line_is_ignored(line):
    """Check if a line from Markdown should be ignored"""
    ignore_lines = [
        config['markdown']['begin_string'],
        config['markdown']['end_string'],
        '| Tag',
        '| ---',
    ]
    for ignore in ignore_lines:
        if line.startswith(ignore):
            return True


def get_readme_table():
    """Return rows from a Markdown table that list tag patterns and deletion
       dates
    """
    md_file = open(config['markdown']['file'], 'r').readlines()
    parsing = False
    items = []
    for line in md_file:
        if line.startswith(config['markdown']['begin_string']):
            parsing = True
        if parsing:
            if not line_is_ignored(line):
                items.append(parse_md_line(line))
        if line.startswith(config['markdown']['end_string']):
            parsing = False

    return items

def parse_date(date):
    """Parse a date string and return a datetime object"""
    return datetime.strptime(date, config['date_format'])


def parse_md_line(md_line):
    """Extract tag patterns and expiration dates from a Markdown table row"""
    _, tags, date = md_line.strip().split('|')
    tags = tags.strip().replace('`', '')
    date = date.strip()
    tags = tags.split(',')
    return { 'tags': tags, 'date': date }

def json_tags():
    """Load a JSON file with tag deletions specified."""
    with open(config['json']['file'], 'r') as f:
        data = list(json.load(f))
        return data


def get_tag_list():
    """Returns a list of tag patterns from the source"""
    tags = []
    if config['json']['file']:
        tags.append(json_tags())
    if config['markdown']['file']:
        tags.append(get_readme_table())
    tags = [i for row in tags for i in row]
    return tags


def tags_to_delete():
    """Return a list of tags to delete based on the deletion date"""
    tags_to_delete = []
    for item in get_tag_list():
        if now >= parse_date(item['date']):
            for pattern in item['tags']:
                pattern = pattern.strip()
                tags_to_delete.append(tags_matching_pattern(pattern))
    # Flatten list
    tags_to_delete = [i for row in tags_to_delete for i in row]
    return tags_to_delete


def delete_expired_tags():
    """Delete tags from the Docker Hub registry using the API"""
    deleted = []
    hub = http.client.HTTPSConnection(config['docker_hub']['api_host'])

    for tag in tags_to_delete():
        headers = {
            "Content-type": "application/json",
            "Authorization": "Bearer %s" % docker_hub_token()
        }

        url = '/v2/namespaces/' + config['docker_hub']['organization'] \
                + '/repositories/' + config['docker_hub']['repository'] \
                + '/tags/' + tag

        hub.request('DELETE', url, headers=headers)
        resp = hub.getresponse()
        content = resp.read().decode()
        deleted.append(tag)
    return deleted


def docker_hub_token():
    """Return an auth token for the Docker Hub API"""

    auth = http.client.HTTPSConnection(config['docker_hub']['api_host'])
    headers = {"Content-type": "application/json"}
    body = json.dumps({
        'username': config['docker_hub']['username'],
        'password': config['docker_hub']['password']
    })
    auth.request('POST', '/v2/users/login', body, headers)
    resp = auth.getresponse()
    content = json.loads(resp.read().decode())
    return content['token']


def tags_matching_pattern(pattern):
    """Compares tags on Docker Hub to our tag patterns and returns a list of
       matching tags that are on Docker Hub
    """

    hub = http.client.HTTPSConnection(config['docker_hub']['api_host'])
    url = '/v2/namespaces/' \
            + config['docker_hub']['organization'] \
            + '/repositories/' \
            + config['docker_hub']['repository'] + '/tags'
    headers = {"Content-type": "application/json"}
    hub.request('GET', url, headers=headers)
    resp = hub.getresponse()
    hub_tags = json.loads(resp.read().decode())

    matching_tags = []
    # TODO: pagination
    for hub_tag in hub_tags['results']:
        if fnmatch.fnmatch(hub_tag['name'], pattern):
            matching_tags.append(hub_tag['name'])
    return matching_tags


if __name__ == "__main__":
    tags = tags_to_delete()
    if len(tags) > 0:
        print(f"Tags to delete: {tags}")
        deleted = delete_expired_tags()
        for tag in tags:
            print(f"> Deleted {config['docker_hub']['organization']}/{config['docker_hub']['repository']}:{tag}")
    else:
        print("There are no tags to delete.")

