# -*- coding: utf-8 -*-
##
## $Id: bfe_fulltext.py,v 1.11 2007/07/20 12:30:27 jerome Exp $
##
## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
##
## CDS Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""BibFormat element - Prints a links to fulltext
"""
    
def format_element(bfo, style='record-illustration-enac'):
    """
    display an icon using provided css class
    @style: css class to appy
    """
    img = """<img src="%s" class="%s" />"""

    urls = bfo.fields("8564_")
    
    icons_urls = []
    
    for complete_url in urls:
        if not complete_url.has_key('u'):
            continue
        url = complete_url['u']
        if not complete_url.has_key('x') or complete_url['x'].lower() != 'icon':
            continue
        icons_urls.append(url)
        
    return '<br />'.join([img % (url, style) for url in icons_urls])

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
