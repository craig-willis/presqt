import base64
import json
import requests

from presqt.targets.github.utilities import validation_check
from presqt.utilities import PresQTError


def github_upload_metadata(token, project_id, metadata_dict):
    """
    Upload the metadata of this PresQT action at the top level of the repo.

    Parameters
    ----------
    token : str
        The user's GitHub token
    project_id : str
        The id of the top level project that the upload took place on
    metadata_dict : dict
        The metadata to be written to the repo
    """
    header, username = validation_check(token)

    file_name = "PRESQT_FTS_METADATA.json"

    metadata_bytes = json.dumps(metadata_dict, indent=4).encode('utf-8')
    base64_metadata = base64.b64encode(metadata_bytes).decode('utf-8')

    put_url = "https://api.github.com/repos/{}/{}/contents/{}".format(username, project_id,
                                                                      file_name)

    data = {
        "message": "PresQT Upload",
        "committer": {
            "name": "PresQT",
            "email": "N/A"},
        "content": base64_metadata}

    response = requests.put(put_url, headers=header, data=json.dumps(data))

    if response.status_code != 201:
        raise PresQTError(
            "The request to create a metadata file has resulted in a {} error code from GitHub.".format(
                response.status_code))
