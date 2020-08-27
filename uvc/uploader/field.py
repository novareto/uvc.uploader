import grok

from dolmen.widget.file import MF as _
from zeam.form.base import interfaces, NO_VALUE, NO_CHANGE
from zeam.form.base.markers import INPUT
from zeam.form.base.widgets import WidgetExtractor
from zeam.form.ztk.fields import (
    SchemaField, SchemaFieldWidget, registerSchemaField)

from zope.size.interfaces import ISized
from zope.schema import Field
from zope.interface import implementer, Interface
from .resources import filer_css, filer_js
from persistent.list import PersistentList
from dolmen.file import NamedFile


grok.templatedir('templates')


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
        print json.dumps(rc)
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
