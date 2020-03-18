# -*- coding: utf-8 -*-
# # Copyright (c) 2007-2011 NovaReto GmbH

import grok
from fanstatic import Library, Resource
from uvc.tbskin.resources import main_css, main_js

library = Library('uvc.uploader', 'static/jquery.filer')

filer_css = Resource(library, 'css/jquery.filer.css')
filer_js = Resource(library, 'js/jquery.filer.min.js', depends=[main_js])
