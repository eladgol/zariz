import logging
import os
import cloudstorage as gcs
from django import http
from google.cloud import storage
from google.cloud.storage import Blob
from google.appengine.api import app_identity
PROJECT_NAME = "zariz-204206"
BUCKET_NAME = "zariz-204206.appspot.com"
class accessGoogleCloudStorage(object):
    def __init__(self, *args, **kwargs):
        self.response = http.HttpResponse()
        self.tmp_filenames_to_clean_up = []
    def get(self):
        self.bucket_name = os.environ.get('BUCKET_NAME',
                                app_identity.get_default_gcs_bucket_name())
        
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.write('Demo GCS Application running from Version: '
        #                + os.environ['CURRENT_VERSION_ID'] + '\n')
        #self.response.write('Using bucket name: ' + bucket_name + '\n\n')
        self.response.content_type = 'text/plain'
        self.response.body = 'Demo GCS Application running from Version: {} \nUsing bucket name: {} \n\n'.format(os.environ['CURRENT_VERSION_ID'], self.bucket_name)

        return self.response

    def create_file(self, filename, data, sContent_type = 'image/jpeg'):
        """Create a file.

        The retry_params specified in the open call will override the default
        retry params for this particular file handle.

        Args:
            filename: filename.
        """
        filename = '/bucket/{}'.format(filename)
        self.response.write('Creating file %s\n' % filename)

        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        gcs_file = gcs.open(filename,
                            'w',
                            content_type=sContent_type,
                            options={'x-goog-meta-foo': 'foo',
                                    'x-goog-meta-bar': 'bar'},
                            retry_params=write_retry_params)
        gcs_file.write(data)
        gcs_file.close()
        
        self.tmp_filenames_to_clean_up.append(filename)
        return filename

    def upload_blob(self, destination_blob_name, data,  sContent_type = 'image/jpeg'):
        """Uploads a file to the bucket."""
        storage_client = storage.Client(PROJECT_NAME)
        bucket = storage_client.get_bucket(BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(data, content_type=sContent_type)
        blob.make_public()
        url = blob.public_url
        print('data uploaded to {} url {}'.format(destination_blob_name, url))
        return url

    def read_file(self, filename):
        self.response.write('Reading the full file contents:\n')
        
        gcs_file = gcs.open(filename)
        contents = gcs_file.read()
        gcs_file.close()
        self.response.write(contents)