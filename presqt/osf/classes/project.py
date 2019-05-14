from rest_framework import status

from presqt.osf.classes.base import OSFBase
from presqt.osf.classes.storage_folder import Storage
from presqt.osf.exceptions import OSFNotFoundError


class Project(OSFBase):
    """
    Class that represents a project in the OSF API.
    """
    def _populate_attributes(self, project):
        """
        Add attributes to the class based on the JSON provided in the API call

        Parameters
        ----------
        project : dict
            Data dictionary returned from the json response to create the Project class instance.
        """

        project = project['data']

        self._endpoint = project['links']['self']
        self.id = project['id']
        self._storages_url = project['relationships']['files']['links']['related']['href']

        attrs = project['attributes']
        self.title = attrs['title']
        self.date_created = attrs['date_created']
        self.date_modified = attrs['date_modified']
        self.description = attrs['description']
        self.size = None
        self.kind = 'container'
        self.kind_name = 'project'

    def __str__(self):
        return '<project [{}]>'.format(self.id)

    def storages(self):
        """
        Iterate over all storages for this project.
        """
        stores_json = self._json(self.session.get(self._storages_url))
        for store in stores_json['data']:
            yield Storage(store, self.session)

    def storage(self, storage):
        """
        Get a storage attached to the project.

        Parameters
        ----------
        storage : str
            Storage name

        Returns
        -------
        Project object.
        """
        for store in self.storages():
            if store.provider == storage:
                return store
        else:
            raise OSFNotFoundError("Project has no storage provider '{}'".format(storage),
                                    status.HTTP_404_NOT_FOUND)

    def get_resources(self, resources):
        """
        Get all project resources. Return in the structure expected for the PresQT API.

        Parameters
        ----------
        resources : list
            Reference to the list of resources we want to add to.

        Returns
        -------
        List of project resources.
        """
        node_obj = {
            'kind': 'container',
            'kind_name': 'project',
            'id': self.id,
            'container': None,
            'title': self.title
        }
        resources.append(node_obj)

        for storage in self.storages():
            storage_obj = {
                'kind': 'container',
                'kind_name': 'storage',
                'id': storage.id,
                'container': self.id,
                'title': storage.title
            }
            resources.append(storage_obj)

            for resource in storage.get_resources_objects(storage.id):
                resources.append(resource)

        return resources