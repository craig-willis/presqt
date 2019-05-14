from presqt.osf.classes.base import OSFBase


class File(OSFBase):
    """
    Class that represents a File in the OSF API.
    """
    def _populate_attributes(self, file):
        """
        Add attributes to the class based on the JSON provided in the API call.

        Parameters
        ----------
        file : dict
            Data dictionary returned from the json response to create the File class instance.
        """
        self.id = file['id']
        # Links
        self._endpoint = file['links']['self']
        self._download_url = file['links']['download']
        self._upload_url = file['links']['upload']
        self._delete_url = file['links']['delete']
        # Attributes
        attrs = file['attributes']
        self.kind = 'item'
        self.kind_name = 'file'
        self.title = attrs['name']
        self.last_touched = attrs['last_touched']
        self.materialized_path = attrs['materialized_path']
        self.date_modified = attrs['date_modified']
        self.current_version = attrs['current_version']
        self.date_created = attrs['date_created']
        self.provider = attrs['provider']
        self.path = attrs['path']
        self.current_user_can_comment = attrs['current_user_can_comment']
        self.guid = attrs['guid']
        self.checkout = attrs['checkout']
        self.tags = attrs['tags']
        self.size = attrs['size']
        # Extra
        extra = attrs['extra']
        self.hashes = extra['hashes']
        self.sha256 = extra['hashes']['sha256']
        self.md5 = extra['hashes']['md5']

    def __str__(self):
        return '<File [{}, {}]>'.format(self.id, self.path)