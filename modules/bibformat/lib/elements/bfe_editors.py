# -*- coding: utf-8 -*-
##
## $Id: bfe_editors.py,v 1.9 2007/02/14 18:32:17 tibor Exp $
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
"""BibFormat element - Print publication info (field 773)
"""

def format(bfo, limit, separator=' ; ', extension='[...]', print_links="yes"):
    """
    Prints the list of editors of a record.
    
    @param limit the maximum number of editors to display
    @param separator the separator between editors.
    @param extension a text printed if more editors than 'limit' exist
    @param print_links if yes, print the editors as HTML link to their publications
    """
    from urllib import quote
    from invenio.config import CFG_SITE_URL
    from invenio import bibrecord
    
    authors = bibrecord.record_get_field_instances(bfo.get_record(), '700')
    editors = [bibrecord.field_get_subfield_values(author, 'a')[0]
               for author in authors if \
               len(bibrecord.field_get_subfield_values(author, "e")) > 0 \
               and bibrecord.field_get_subfield_values(author, "e")[0]=="ed."
              ]
    if print_links.lower() == "yes":
        editors = ['<a href="' + CFG_SITE_URL + '/search?f=author&p=' + \
                   quote(editor) + \
                   '&amp;ln='+ bfo.lang + \
                   '">' + editor + '</a>'
                   for editor in editors if editor.strip()]

    if len(editors) == 0:
        beginning = ''
        ending = ''
    elif len(editors) == 1:
        beginning = ''
        ending = ' (ed.)'
    else:
        beginning = ''
        ending = ' (eds.)'

    if limit.isdigit() and len(editors) > int(limit):
        return beginning + separator.join(editors[:int(limit)]) + extension + ending

    elif len(editors) > 0:
        return beginning + separator.join(editors) + ending