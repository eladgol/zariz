import logging
import os
#import cloudstorage as gcs
from django import http
from google.cloud import storage
from google.cloud.storage import Blob
#from google.appengine.api import app_identity

PROJECT_NAME = "zariz-204206"
BUCKET_NAME = "zariz-204206.appspot.com"
#pip install cloudstorage -t lib
#pip install opuslib==2.0.0

def agcs_get():
    #bucket_name = os.environ.get('BUCKET_NAME',
    #                       app_identity.get_default_gcs_bucket_name())
    
    #response.headers['Content-Type'] = 'text/plain'
    #response.write('Demo GCS Application running from Version: '
    #               + os.environ['CURRENT_VERSION_ID'] + '\n')
    #response.write('Using bucket name: ' + bucket_name + '\n\n')
    #response.content_type = 'text/plain'
    #response.body = 'Demo GCS Application running from Version: {} \nUsing bucket name: {} \n\n'.format(os.environ['CURRENT_VERSION_ID'], bucket_name)

    #return bucket_name
    return BUCKET_NAME

def upload_blob(destination_blob_name, data,  sContent_type = 'image/jpeg'):
    """Uploads a file to the bucket."""
    storage_client = storage.Client(PROJECT_NAME)
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(data, content_type=sContent_type)
    blob.make_public()
    url = blob.public_url
    print('data uploaded to {} url {}'.format(destination_blob_name, url))
    return url

# def upload_blob_GAE(destination_blob_name, data,  sContent_type = 'image/jpeg'):
#     """Uploads a file to the bucket."""

#     bucket = agcs_get()
   
#     write_retry_params = gcs.RetryParams(backoff_factor=1.1)
#     #gcs_file = gcs.open(filename,
#     #                  'w',
#     #                  content_type=sContent_type,
#     #                  options={'x-goog-meta-foo': 'foo',
#     #                           'x-goog-meta-bar': 'bar'},
#     #                  retry_params=write_retry_params)

#     #gcs_file.write(data)
#     #gcs_file.close()
    
#     #print('data uploaded to {} url {}'.format(destination_blob_name, url))
#     #return url
#     return ""

