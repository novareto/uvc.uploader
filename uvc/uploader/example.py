# -*- coding: utf-8 -*-
# # Copyright (c) 2007-2019 NovaReto GmbH
# # cklinger@novareto.de 

import grok
import uvcsite

from zope import interface, schema
import dolmen.file

class IPerson(interface.Interface):

    name = schema.TextLine(
        title=u"Name",
        description=u"Give us the Name",
        )

    files = schema.List(
        title=u"Files",
        description=u"Please Upload some Files here",
        value_type=dolmen.file.FileField(
            title=u"File",
            description=u"FILE"
            )
        )


class PersonForm(uvcsite.Form):
    grok.context(interface.Interface)

    fields = uvcsite.Fields(IPerson)

    @uvcsite.action('Save')
    def handle_save(self):
        data, errors = self.extractData()
        print data
        print errors

