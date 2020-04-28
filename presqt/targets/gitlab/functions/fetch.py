import requests
from rest_framework import status

from presqt.targets.gitlab.utilities.gitlab_paginated_data import gitlab_paginated_data
from presqt.targets.gitlab.utilities.validation_check import validation_check
from presqt.targets.gitlab.utilities.get_gitlab_project_data import get_gitlab_project_data
from presqt.utilities import PresQTResponseException


def gitlab_fetch_resources(token, search_parameter):
    """
    Fetch all users projects from GitLab.

    Parameters
    ----------
    token : str
        User's GitLab token
    search_parameter : dict
        The search parameter passed to the API View
        Gets passed formatted as {'title': 'search_info'}

    Returns
    -------
    List of dictionary objects that represent GitLab resources.
    Dictionary must be in the following format:
        {
            "kind": "container",
            "kind_name": "folder",
            "id": "12345",
            "container": "None",
            "title": "Folder Name",
        }
    """
    base_url = "https://gitlab.com/api/v4/"
    try:
        headers, user_id = validation_check(token)
    except PresQTResponseException:
        raise PresQTResponseException("Token is invalid. Response returned a 401 status code.",
                                      status.HTTP_401_UNAUTHORIZED)

    if search_parameter:
        if 'author' in search_parameter:
            author_url = "{}users?username={}".format(base_url, search_parameter['author'])
            author_response_json = requests.get(author_url, headers=headers).json()
            if not author_response_json:
                return []
            data = requests.get(
                "https://gitlab.com/api/v4/users/{}/projects".format(author_response_json[0]['id']),
                headers=headers).json()

        elif 'general' in search_parameter:
            search_url = "{}search?scope=projects&search={}".format(
                base_url, search_parameter['general'])
            data = requests.get(search_url, headers=headers).json()

        elif 'id' in search_parameter:
            project_url = "{}projects/{}".format(base_url, search_parameter['id'])
            project_response = requests.get(project_url, headers=headers)

            if project_response.status_code == 404:
                return []
            data = [project_response.json()]

        elif 'title' in search_parameter:
            title_url = "{}/projects?search={}".format(base_url, search_parameter['title'])
            data = requests.get(title_url, headers=headers).json()

    else:
        data = gitlab_paginated_data(headers, user_id)

    return get_gitlab_project_data(data, headers, [])


def gitlab_fetch_resource(token, resource_id):
    """
    Fetch the GitLab resource matching the resource_id given.

    Parameters
    ----------
    token : str
        User's GitLab token

    resource_id : str
        ID of the resource requested

    Returns
    -------
    A dictionary object that represents the GitLab resource.
    Dictionary must be in the following format:
    {
        "kind": "container",
        "kind_name": "project",
        "id": "12345",
        "title": "23296359282_934200ec59_o.jpg",
        "date_created": "2019-05-13T14:54:17.129170Z",
        "date_modified": "2019-05-13T14:54:17.129170Z",
        "hashes": {
            "md5": "aaca7ef067dcab7cb8d79c36243823e4",
        },
        "extra": {
            "any": extra,
            "values": here
        }
    }
    """
    try:
        headers, user_id = validation_check(token)
    except PresQTResponseException:
        raise PresQTResponseException("Token is invalid. Response returned a 401 status code.",
                                      status.HTTP_401_UNAUTHORIZED)
    partitioned_id = resource_id.partition(':')

    if ':' in resource_id:
        project_id = partitioned_id[0]
        project_url = "https://gitlab.com/api/v4/projects/{}".format(project_id)

        response = requests.get(project_url, headers=headers)
        if response.status_code != 200:
            raise PresQTResponseException("The resource could not be found by the requesting user.",
                                          status.HTTP_404_NOT_FOUND)
        path_to_resource = partitioned_id[2].replace(
            '%252F', '%2F').replace('%252E', '%2E').replace('+', ' ')
        string_path_to_resource = path_to_resource.replace('%2F', '/').replace('%2E', '.')

        # Figure out the resource type (file, folder)
        tree_url = 'https://gitlab.com/api/v4/projects/{}/repository/tree?recursive=1'.format(
            project_id)
        file_data = gitlab_paginated_data(headers, None, tree_url)
        resource_type = 'folder'
        for data in file_data:
            if data['path'] == string_path_to_resource:
                if data['type'] == 'blob':
                    resource_type = 'file'

        # Resource is a file
        if resource_type == 'file':
            response = requests.get(
                'https://gitlab.com/api/v4/projects/{}/repository/files/{}?ref=master'.format(
                    project_id, path_to_resource), headers=headers)

            data = response.json()
            resource = {
                "kind": "item",
                "kind_name": "file",
                "id": resource_id,
                "title": data['file_name'],
                "date_created": None,
                "date_modified": None,
                "hashes": {'sha256': data['content_sha256']},
                "extra": {'ref': data['ref'], 'commit_id': data['commit_id'], 'size': data['size']}}

        # Resource is a folder
        else:
            response = requests.get(
                'https://gitlab.com/api/v4/projects/{}/repository/tree?path={}'.format(
                    project_id, path_to_resource), headers=headers)
            # If the directory doesn't exist, they return an empty list
            if response.json() == []:
                raise PresQTResponseException("The resource could not be found by the requesting user.",
                                              status.HTTP_404_NOT_FOUND)
            resource = {
                "kind": "container",
                "kind_name": "dir",
                "id": resource_id,
                "title": path_to_resource.rpartition('%2F')[2].replace('%2E', '.'),
                "date_created": None,
                "date_modified": None,
                "hashes": {},
                "extra": {}}

    # This is the top level project
    else:
        project_url = "https://gitlab.com/api/v4/projects/{}".format(resource_id)

        response = requests.get(project_url, headers=headers)
        if response.status_code != 200:
            raise PresQTResponseException("The resource could not be found by the requesting user.",
                                          status.HTTP_404_NOT_FOUND)

        data = response.json()

        resource = {
            "kind": "container",
            "kind_name": "project",
            "id": data['id'],
            "title": data['name'],
            "date_created": data['created_at'],
            "date_modified": data['last_activity_at'],
            "hashes": {},
            "extra": {}
        }
        for key, value in data.items():
            if '_url' in key:
                pass
            else:
                resource['extra'][key] = value

    return resource