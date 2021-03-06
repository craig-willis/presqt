from rest_framework import status

from presqt.targets.osf.utilities import get_osf_resource
from presqt.utilities import PresQTResponseException, PresQTInvalidTokenError, PresQTValidationError
from presqt.targets.osf.classes.main import OSF


def osf_fetch_resources(token, search_parameter):
    """
    Fetch all OSF resources for the user connected to the given token.

    Parameters
    ----------
    token : str
        User's OSF token
    search_parameter : dict
        The search parameter passed to the API View
        Gets passed formatted as {'title': 'search_info'}

    Returns
    -------
    List of dictionary objects that represent OSF resources.
    Dictionary must be in the following format:
        {
            "kind": "container",
            "kind_name": "folder",
            "id": "12345",
            "container": "None",
            "title": "Folder Name",
        }
    """
    try:
        osf_instance = OSF(token)
    except PresQTInvalidTokenError:
        raise PresQTResponseException("Token is invalid. Response returned a 401 status code.",
                                      status.HTTP_401_UNAUTHORIZED)

    if search_parameter:
        if 'title' in search_parameter:
            # Format the search that is coming in to be passed to the OSF API
            search_parameters = search_parameter['title'].replace(' ', '+')
            url = 'https://api.osf.io/v2/nodes/?filter[title]={}'.format(search_parameters)
        elif 'id' in search_parameter:
            url = 'https://api.osf.io/v2/nodes/?filter[id]={}'.format(search_parameter['id'])
    else:
        url = None
    try:
        resources = osf_instance.get_resources(url)
    except PresQTValidationError as e:
        raise e
    return resources


def osf_fetch_resource(token, resource_id):
    """
    Fetch the OSF resource matching the resource_id given.

    Parameters
    ----------
    token : str
        User's OSF token

    resource_id : str
        ID of the resource requested

    Returns
    -------
    A dictionary object that represents the OSF resource.
    Dictionary must be in the following format:
    {
        "kind": "item",
        "kind_name": "file",
        "id": "12345",
        "title": "23296359282_934200ec59_o.jpg",
        "date_created": "2019-05-13T14:54:17.129170Z",
        "date_modified": "2019-05-13T14:54:17.129170Z",
        "hashes": {
            "md5": "aaca7ef067dcab7cb8d79c36243823e4",
            "sha256": "ea94ce54261720c16abb508c6dcd1fd481c30c09b7f2f5ab0b79e3199b7e2b55"
        },
        "extra": {
            "any": "extra",
            "values": "here"
        }
    }
    """
    try:
        osf_instance = OSF(token)
    except PresQTInvalidTokenError:
        raise PresQTResponseException("Token is invalid. Response returned a 401 status code.",
                                      status.HTTP_401_UNAUTHORIZED)

    def create_object(resource_object):
        resource_object_obj = {
            'kind': resource_object.kind,
            'kind_name': resource_object.kind_name,
            'id': resource_object.id,
            'title': resource_object.title,
            'date_created': resource_object.date_created,
            'date_modified': resource_object.date_modified,
            'hashes': {
                'md5': resource_object.md5,
                'sha256': resource_object.sha256
            },
            'extra': {}
        }

        if resource_object.kind_name in ['folder', 'file']:
            resource_object_obj['extra'] = {
                'last_touched': resource_object.last_touched,
                'materialized_path': resource_object.materialized_path,
                'current_version': resource_object.current_version,
                'provider': resource_object.provider,
                'path': resource_object.path,
                'current_user_can_comment': resource_object.current_user_can_comment,
                'guid': resource_object.guid,
                'checkout': resource_object.checkout,
                'tags': resource_object.tags,
                'size': resource_object.size
            }
        elif resource_object.kind_name == 'project':
            resource_object_obj['extra'] = {
                'category': resource_object.category,
                'fork': resource_object.fork,
                'current_user_is_contributor': resource_object.current_user_is_contributor,
                'preprint': resource_object.preprint,
                'current_user_permissions': resource_object.current_user_permissions,
                'custom_citation': resource_object.custom_citation,
                'collection': resource_object.collection,
                'public': resource_object.public,
                'subjects': resource_object.subjects,
                'registration': resource_object.registration,
                'current_user_can_comment': resource_object.current_user_can_comment,
                'wiki_enabled': resource_object.wiki_enabled,
                'node_license': resource_object.node_license,
                'tags': resource_object.tags,
                'size': resource_object.size
            }
        return resource_object_obj

    # Get the resource
    resource = get_osf_resource(resource_id, osf_instance)

    return create_object(resource)
