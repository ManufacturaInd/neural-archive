from gluon import current

# thumbnail recipe from
# http://movu.ca/demo/article/show/36/creating-thumbnails-with-web2py
 
def thumber(image, nx=300, ny=2000, name='medium'):
    if image:
        try:
            request = current.request
            from PIL import Image
            import os
            img = Image.open(request.folder + 'uploads/' + image)
            img.thumbnail((nx, ny), Image.ANTIALIAS)
            root, ext = os.path.splitext(image)
            if 'tif' in ext:
                ext = ".jpg"
            thumb = '%s_%s%s' % (root, name, ext)
            img.save(request.folder + 'uploads/' + thumb)
            return thumb
        except Exception:
            return image
