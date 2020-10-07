import grok
import transaction

from persistent import Persistent
from persistent.list import PersistentList
from zeam.form.base import interfaces, NO_VALUE, NO_CHANGE
from zeam.form.base.markers import INPUT
from zeam.form.base.widgets import WidgetExtractor
from zeam.form.ztk.fields import SchemaField, SchemaFieldWidget, registerSchemaField
from zope.contenttype import guess_content_type
from zope.interface import Interface, implementer
from zope.schema import Field
from zope.schema.fieldproperty import FieldProperty

from .chunk import FileChunk
from .interfaces import IDataChunk, INamedFile
from .resources import filer_css, filer_js
from .utils import clean_filename


grok.templatedir('templates')


# set the size of the chunks
MAXCHUNKSIZE = 1 << 16


@implementer(INamedFile)
class NamedFile(Persistent):
    """A simple INamedFile implementation that can guess the content type
    from the value and the filename.
    """
    filename = FieldProperty(INamedFile['filename'])

    def __init__(self, data=b'', contentType='', filename=None):
        self.data = data
        if filename is not None:
            self.filename = clean_filename(filename)
        if not contentType and filename:
            # If we handle large files, we don't want them read just
            # to guess the content type. We provide only the filename.
            self.contentType, enc = guess_content_type(name=filename)
        else:
            self.contentType = contentType

    @property
    def data(self):
        """Property in charge of setting and getting the file data.
        """
        if IDataChunk.providedBy(self._data):
            return str(self._data)
        return self._data

    @data.setter
    def data(self, data):
        # Handle case when data is a string
        if isinstance(data, unicode):
            data = data.encode('UTF-8')

        if isinstance(data, str):
            self._data, self._size = FileChunk(data), len(data)
            return

        # Handle case when data is None
        if data is None:
            raise TypeError('Cannot set None data on a file.')

        # Handle case when data is already a FileChunk
        if isinstance(data, FileChunk):
            size = len(data)
            self._data, self._size = data, size
            return

        # Handle case when data is a file object
        seek = data.seek
        read = data.read

        seek(0, 2)
        size = end = data.tell()

        if size <= 2 * MAXCHUNKSIZE:
            seek(0)
            if size < MAXCHUNKSIZE:
                self._data, self._size = read(size), size
                return
            self._data, self._size = FileChunk(read(size)), size
            return

        # Make sure we have an _p_jar, even if we are a new object, by
        # doing a sub-transaction commit.
        transaction.savepoint(optimistic=True)

        jar = self._p_jar

        if jar is None:
            # Ugh
            seek(0)
            self._data, self._size = FileChunk(read(size)), size
            return

        # Now we're going to build a linked list from back
        # to front to minimize the number of database updates
        # and to allow us to get things out of memory as soon as
        # possible.
        next = None
        while end > 0:
            pos = end - MAXCHUNKSIZE
            if pos < MAXCHUNKSIZE:
                pos = 0 # we always want at least MAXCHUNKSIZE bytes
                seek(pos)
                data = FileChunk(read(end - pos))

            # Woooop Woooop Woooop! This is a trick.
            # We stuff the data directly into our jar to reduce the
            # number of updates necessary.
            jar.add(data)

            # This is needed and has side benefit of getting
            # the thing registered:
            data.next = next

            # Now make it get saved in a sub-transaction!
            transaction.savepoint(optimistic=True)

            # Now make it a ghost to free the memory.  We
            # don't need it anymore!
            data._p_changed = None

            next = data
            end = pos

        self._data, self._size = next, size
        return

    @property
    def size(self):
        return self._size


class IFilesField(Interface):
    """A field storing binary datas.
    """


@implementer(IFilesField)
class FilesField(Field):
    """A field handling multiple file representation
    """
    missing_value = []


class IFilesWidget(interfaces.IFieldWidget):
    """A widget that represents a list of files.
    """


class FilesSchemaField(SchemaField):
    """Files field.
    """
    htmlAttributes = {
        'data-jfiler-changeInput': 'true',
        'data-jfiler-showThumbs': 'true',
    }


@implementer(IFilesWidget)
class FilesWidget(SchemaFieldWidget):
    grok.adapts(FilesSchemaField, interfaces.IFormData, Interface)
    grok.template(str(INPUT))

    def prepareContentValue(self, value):
        if value is NO_VALUE or value is None:
            return {self.identifier: False}
        return {self.identifier: True}

    def update(self):
        filer_css.need()
        filer_js.need()

        #if not self.form.ignoreContent:
        ##    raise NotImplementedError("Files can't be represented.")

        SchemaFieldWidget.update(self)

    def getFiles(self):
        import json
        content = self.form.getContentData().getContent()
        if getattr(content, self.component._field.getName(), None):
            rc = [{
                'url': '%s/++download++%s' % (
                    grok.url(self.request, content),
                    fileobj.filename),
                'name': fileobj.filename,
                'size': fileobj.size,
                'type': fileobj.contentType
            } for fileobj in self.component._field.get(content)]
        else:
            rc = []
        return json.dumps(rc)


class FileWidgetExtractor(WidgetExtractor):
    """A value extractor for a file widget (including image)
    """
    grok.adapts(FilesSchemaField, interfaces.IFormData, Interface)

    def extract(self):
        content = self.form.getContentData().getContent()
        existing = getattr(content, self.component._field.getName())
        value = self.request.form.get(self.identifier + '[]') or NO_VALUE
        if not isinstance(value, list):
            if value is NO_VALUE:
                value = []
            else:
                 value = [value]
        existing.extend([
            NamedFile(x.read(), filename=x.filename) for x in value
        ])
        return (existing, None)


def register():
    """Entry point hook.
    """
    registerSchemaField(FilesSchemaField, IFilesField)
