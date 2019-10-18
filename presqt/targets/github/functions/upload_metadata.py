import base64
import fnmatch
import json
import os
import re
import requests

from natsort import natsorted
from rest_framework import status

from presqt.targets.github.utilities import validation_check, github_paginated_data
from presqt.utilities import PresQTResponseException


def github_upload_metadata(token, resource_id, resource_main_dir, metadata_dict, repo_id=None):
    """
    Upload the metadata of this PresQT action at the top level of the repo.

    Parameters
    ----------
    token : str
        The user's GitHub token
    resource_id : str
        An id the upload is taking place on (not used for GitHub)
    resource_main_dir : str
        The path to the bag to be uploaded
    metadata_dict : dict
        The metadata to be written to the repo
    repo_id : str
        The id of the new repo that has been created
    """
    # Uploading to an existing Github repository is not allowed
    if resource_id:
        raise PresQTResponseException("Can't upload to an existing Github repository.",
                                      status.HTTP_400_BAD_REQUEST)
    try:
        header, username = validation_check(token)
    except PresQTResponseException:
        raise PresQTResponseException('The response returned a 401 unauthorized status code.',
                                      status.HTTP_401_UNAUTHORIZED)

    file_name = "PRESQT_FTS_METADATA.json"

    metadata_bytes = json.dumps(metadata_dict, indent=4).encode('utf-8')
    base64_metadata = base64.b64encode(metadata_bytes).decode('utf-8')

    put_url = "https://api.github.com/repos/{}/{}/contents/{}".format(username, repo_id, file_name)

    data = {
        "message": "PresQT Upload",
        "committer": {
            "name": "PresQT",
            "email": "N/A"},
        "content": base64_metadata}

    requests.put(put_url, headers=header, data=json.dumps(data))
