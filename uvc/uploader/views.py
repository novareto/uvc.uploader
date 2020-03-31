# -*- coding: utf-8 -*-
# # Copyright (c) 2007-2019 NovaReto GmbH
# # cklinger@novareto.de

import grok
import uvcsite

from zope import interface, schema
from .field import FilesField
from dolmen.file.file import NamedFile


class IPerson(interface.Interface):

    name = schema.TextLine(
        title=u"Name",
        description=u"Give us the Name",
    )

    files = FilesField(
        title=u"Files",
        description=u"Please Upload some Files here",
        required=True,
    )


class PersonForm(uvcsite.Form):
    grok.name('pf')
    grok.context(uvcsite.IUVCSite)

    fields = uvcsite.Fields(IPerson)
    fields['files'].htmlAttributes.update({'data-jfiler-extensions': 'jpg, pdf'})
    status = ""

    @uvcsite.action('Save')
    def handle_save(self):
        data, errors = self.extractData()
        files = data.pop('files')
        if files is not None:
            fobjs = [NamedFile(data=fd, filename=fd.filename)
                     for fd in files]

        print data, fobjs
        print errors
