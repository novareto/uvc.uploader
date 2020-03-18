import grokcore.view as grok

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


grok.templatedir('templates')


class IFilesField(Interface):
    """A field storing binary datas.
    """


@implementer(IFilesField)
class FilesField(Field):
    """A field handling multiple file representation
    """


class IFilesWidget(interfaces.IFieldWidget):
    """A widget that represents a list of files.
    """


class FilesSchemaField(SchemaField):
    """Files field.
    """


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

        if not self.form.ignoreContent:
            raise NotImplementedError("Files can't be represented.")

        SchemaFieldWidget.update(self)


class FileWidgetExtractor(WidgetExtractor):
    """A value extractor for a file widget (including image)
    """
    grok.adapts(FilesSchemaField, interfaces.IFormData, Interface)

    def extract(self):
        value = self.request.form.get(self.identifier + '[]') or NO_VALUE
        if not isinstance(value, list):
            value = [value]
        return (value, None)


def register():
    """Entry point hook.
    """
    registerSchemaField(FilesSchemaField, IFilesField)
