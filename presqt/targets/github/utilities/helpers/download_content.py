import requests


def download_content(username, url, header, repo_name, files):
    """
    Recursive function to extract all files from a given repo.

    Parameters
    ----------
    username : str
        The user's GitHub username.
    url : str
        The url of the repo's contents
    header: dict
        API header expected by GitHub
    repo_name : str
        The name of the repo that is being downloaded
    files : list
        A list of dictionaries with file information

    Returns
    -------
    A list of file dictionaries and a list of empty containers
    """
    initial_data = requests.get(url, headers=header).json()
    action_metadata = {"sourceUsername": username}
    # Loop through the initial data and build up the file urls and if the type is directory
    # recursively call function.
    for data in initial_data:
        if data['type'] == 'file':
            file_metadata = {"commit_hash": data['sha']}
            for key, value in data.items():
                if key not in ['name', 'path', 'sha']:
                    file_metadata[key] = value

            files.append({
                'file': data['download_url'],
                'hashes': {},
                'title': data['name'],
                'path': '/{}/{}'.format(repo_name, data['path']),
                'source_path': '/{}/{}'.format(repo_name, data['path']),
                'extra_metadata': file_metadata})
        else:
            download_content(username, data['url'], header, repo_name, files)

    return files, [], action_metadata
