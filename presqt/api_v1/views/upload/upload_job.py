import json
import multiprocessing

from dateutil.relativedelta import relativedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from presqt.api_v1.utilities import (get_destination_token, get_process_info_data,
                                     process_token_validation, hash_tokens)
from presqt.utilities import PresQTValidationError, write_file, read_file


class UploadJob(APIView):
    """
    **Supported HTTP Methods**

    * GET:
        - Check if a given resource upload is finished.
    """

    def get(self, request, ticket_number):
        """
        Check in on the resource's upload process state.

        Parameters
        ----------
        ticket_number : str
            The ticket number of the upload being prepared.

        Returns
        -------
        200: OK
        {
            "status_code": "200",
            "message": "Upload successful",
            "failed_fixity": [],
            "resources_ignored": [],
            "resources_updated": []
        }

        202: Accepted
        {
            "status_code": null,
            "message": "Upload is being processed on the server"
        }

        400: Bad Request
        {
            "error": "PresQT Error: 'presqt-destination-token' missing in the request headers."
        }

        401: Unauthorized
        {
            "error": "PresQT Error: Header 'presqt-destination-token' does not match the
            'presqt-destination-token' for this server process."
        }

        404: Not Found
        {
            "error": "PresQT Error: Invalid ticket number, '1234'."
        }

        500: Internal Server Error
        {
            "status_code": "404",
            "message": "Resource with id 'bad_id' not found for this user."
        }
        """
        # Perform token validation. Read data from the process_info file.
        try:
            token = get_destination_token(request)
            process_data = get_process_info_data('uploads', ticket_number)
            process_token_validation(hash_tokens(token), process_data, 'presqt-destination-token')
        except PresQTValidationError as e:
            return Response(data={'error': e.data}, status=e.status_code)

        upload_status = process_data['status']
        data = {'status_code': process_data['status_code'], 'message': process_data['message']}

        if upload_status == 'finished':
            http_status = status.HTTP_200_OK
            data['failed_fixity'] = process_data['failed_fixity']
            data['resources_ignored'] = process_data['resources_ignored']
            data['resources_updated'] = process_data['resources_updated']
        else:
            if upload_status == 'in_progress':
                http_status = status.HTTP_202_ACCEPTED
            else:
                http_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(status=http_status, data=data)

    def patch(self, request, ticket_number):
        """
        Cancel the resource upload process on the server. Update the process_info.json
        file appropriately.

        Parameters
        ----------
        ticket_number : str
            The ticket number of the upload being prepared.

        Returns
        -------
        200: OK
        {
            "status_code": "499",
            "message": "Upload was cancelled by the user"
        }

        400: Bad Request
        {
            "error": "'presqt-destination-token' missing in the request headers."
        }

        401: Unauthorized
        {
            "error": "Header 'presqt-destination-token' does not match the
            'presqt-destination-token' for this server process."
        }

        404: Not Found
        {
            "error": "Invalid ticket number, '1234'."
        }

        406: Not Acceptable
        {
            "status_code": "200",
            "message": "Upload Successful"
        }
        """
        # Perform token validation. Read data from the process_info file.
        try:
            token = get_destination_token(request)
            data = get_process_info_data('uploads', ticket_number)
            process_token_validation(hash_tokens(token), data, 'presqt-destination-token')
        except PresQTValidationError as e:
            return Response(data={'error': e.data}, status=e.status_code)

        # Wait until the spawned off process has started to cancel the upload
        while data['function_process_id'] is None:
            try:
                data = get_process_info_data('uploads', ticket_number)
            except json.decoder.JSONDecodeError:
                # Pass while the process_info file is being written to
                pass

        # If upload is still in progress then cancel the subprocess
        if data['status'] == 'in_progress':
            for process in multiprocessing.active_children():
                if process.pid == data['function_process_id']:
                    process.kill()
                    process.join()
                    data['status'] = 'failed'
                    data['message'] = 'Upload was cancelled by the user'
                    data['status_code'] = '499'
                    data['expiration'] = str(timezone.now() + relativedelta(hours=1))
                    process_info_path = 'mediafiles/uploads/{}/process_info.json'.format(
                        ticket_number)
                    write_file(process_info_path, data, True)
                    return Response(
                        data={'status_code': data['status_code'], 'message': data['message']},
                        status=status.HTTP_200_OK)
        # If upload is finished then don't attempt to cancel subprocess
        else:
            return Response(
                data={'status_code': data['status_code'], 'message': data['message']},
                status=status.HTTP_406_NOT_ACCEPTABLE)