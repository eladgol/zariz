import requests

from django.core import files

# List of images to download
#image_urls = [
#    'http://i.thegrindstone.com/wp-content/uploads/2013/01/how-to-get-awesome-back.jpg',
#]
def downloadImageToBuff(image_url):
    # Steam the image from the url
    request = requests.get(image_url, stream=True)
    # Was the request OK?
    if request.status_code != requests.codes.ok:
        # Nope, error handling, skip file etc etc etc
        return -1

    # Get the filename from the url, used for saving later
   # file_name = image_url.split('/')[-1]
    sz = 0
    buff = b""
    # Read the streamed image in sections
    for block in request.iter_content(1024 * 8):

        # If no more file then stop
        if not block:
            break
        sz += len(block)
        # Write image block to temporary file
        buff+=block

    contentType = request.headers['content-type']
    ContentLength = request.headers['content-length']
    
    return buff, contentType, ContentLength
    