__author__ = 'wpl'
import os
from urllib import quote, unquote

from django.core.files import File
from django.core.files.storage import default_storage
from django.conf import settings
from django import template

try:
    from json import loads
except ImportError:  # Python < 2.6
    from django.utils.simplejson import loads

# Try to import PIL in either of the two ways it can end up installed.
try:
    from PIL import Image, ImageFile, ImageOps
except ImportError:
    import Image
    import ImageFile
    import ImageOps

register = template.Library()

class FileSystemEncodingChanged(RuntimeError):
    def __init__(self):
        msg = ("Access was attempted on a file that contains unicode "
               "characters in its path, but somehow the current locale "
               "does not support utf-8. You may need to set 'LC_ALL' "
               "to a correct value, eg: 'en_US.UTF-8'.")
        RuntimeError.__init__(self, msg)

@register.simple_tag
def thumbnail(image_url, width, height, quality=95):
    """
    Given the URL to an image, resizes the image using the given width and
    height on the first time it is requested, and returns the URL to the new
    resized image. if width or height are zero then original ratio is
    maintained.
    """
    if not image_url:
        return ""

    image_url = unquote(unicode(image_url))
    print image_url
    if image_url.startswith(settings.MEDIA_URL):
        print 'startswith = TRUE'
        image_url = image_url.replace(settings.MEDIA_URL, "", 1)
    else:
        print 'startswith =FALSE'
    print image_url
    image_dir, image_name = os.path.split(image_url)
    image_prefix, image_ext = os.path.splitext(image_name)
    filetype = {".png": "PNG", ".gif": "GIF"}.get(image_ext, "JPEG")
    thumb_name = "%s-%sx%s%s" % (image_prefix, width, height, image_ext)
    print thumb_name
    thumb_dir = os.path.join(settings.MEDIA_ROOT, image_dir,
                             settings.THUMBNAILS_DIR_NAME)
    print thumb_dir
    if not os.path.exists(thumb_dir):
        os.makedirs(thumb_dir)
    thumb_path = os.path.join(thumb_dir, thumb_name)
    thumb_url = "%s/%s" % (settings.THUMBNAILS_DIR_NAME,
                           quote(thumb_name.encode("utf-8")))
    image_url_path = os.path.dirname(image_url)
    print image_url_path
    if image_url_path:
        thumb_url = "%s/%s" % (image_url_path, thumb_url)

    print thumb_url
    try:
        thumb_exists = os.path.exists(thumb_path)
    except UnicodeEncodeError:
        # The image that was saved to a filesystem with utf-8 support,
        # but somehow the locale has changed and the filesystem does not
        # support utf-8.
        print 'UNICODEERROR'
        raise FileSystemEncodingChanged()
    if thumb_exists:
        # Thumbnail exists, don't generate it.
        print 'thumb exists'
        return thumb_url
    elif not default_storage.exists(image_url):
        print 'default storage DNA'
        # Requested image does not exist, just return its URL.
        return image_url

    f = default_storage.open(image_url)
    try:
        image = Image.open(f)
        print 'opening image'
    except:
        # Invalid image format
        print 'invalid format'
        return image_url

    image_info = image.info
    print image.info
    print image.mode
    width = int(width)
    height = int(height)
    print 'width: %d X height: %d' % (width, height)

    # If already right size, don't do anything.
    if width == image.size[0] and height == image.size[1]:
        return image_url
    # Set dimensions.
    if width == 0:
        width = image.size[0] * height / image.size[1]
    elif height == 0:
        height = image.size[1] * width / image.size[0]
    #TODO: THIS IS THROWING I0Exception Error, zip or jpeg libs not available
    #if image.mode not in ("P", "L", "RGBA"):
    #    image = image.convert("RGBA")
    # Required for progressive jpgs.
    ImageFile.MAXBLOCK = 2 * (max(image.size) ** 2)
    try:
        image = image.thumbnail(width, height, Image.ANTIALIAS)
        image = image.save(thumb_path, filetype, quality=quality, **image_info)
        print 'thumb_path: %s, filetype: %s' % (thumb_path, filetype)
        # Push a remote copy of the thumbnail if MEDIA_URL is
        # absolute.
        if "://" in settings.MEDIA_URL:
            print ':// in settings.MEDIA_URL'
            with open(thumb_path, "r") as f:
                default_storage.save(thumb_url, File(f))
    except Exception:
        print 'there was an exception'
        # If an error occurred, a corrupted image may have been saved,
        # so remove it, otherwise the check for it existing will just
        # return the corrupted image next time it's requested.
        return image_url
    print image_url
    print thumb_url
    return thumb_url

