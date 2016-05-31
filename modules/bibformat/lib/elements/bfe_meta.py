# -*- coding: utf-8 -*-
##
## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008 CERN.
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
"""BibFormat element -

"""
__revision__ = "$Id$"

from invenio.bibformat_utils import parse_tag
from invenio.htmlutils import create_html_tag
from invenio.bibindex_engine import get_field_tags

def format_element(bfo, name, tag_name='', tag = '', respect_file_visiblity=False, author_only=True, escape=4):
    """Prints a custom field in a way suitable to be used in HTML META
    tags.  In particular conforms to Google Scholar harvesting protocol as
    defined http://scholar.google.com/intl/en/scholar/inclusion.html


    @param tag_name: the name, from tag table, of the field to be exported
    looks initially for names prefixed by "meta-"<tagname>
    then looks for exact name, then falls through to "tag"
    @param tag: the MARC tag to be exported (only if not defined by tag_name)
    @param name: name to be displayed in the meta headers, labelling this value
    @param respect_file_visiblity: check the 8564_z if we are allowed to show a file
    @param author_only: as google scholar, the author field is for authors only, 
                        not editor nor director
    """
    
    # for files case, make different rule
    if respect_file_visiblity:
        values = []

        files = bfo.fields('8564_')

        for file_dict in files:
            # show only public
            if file_dict.get('x'):
                try:
                    if file_dict['x'] == 'PUBLIC':
                        values.append(file_dict['u'])
                except KeyError:
                    continue
    else:
        tags = []
        if tag_name:
            # First check for special meta named tags
            tags = get_field_tags("meta-" + tag_name)
            if not tags:
                #then check for regular tags
                tags = get_field_tags(tag_name)
        if not tags and tag:
            # fall back to explicit marc tag
            tags = [tag]
        if not tags:
            return ''
        
        # load values to be printed
        values = []
        
        for marctag in tags:
            ######################################
            # Special cases
            if marctag == '700__a' and author_only:
                # authors
                # no editor or director
                authors_info = bfo.fields('700',escape=2)
                for author_info in authors_info:
                    if author_info.has_key('a') and not author_info.has_key('e'):
                        values.append(author_info['a'])
            # doi                        
            elif marctag == '0247_a':
                # dont show anything that is not an doi
                doi_infos =  bfo.fields('0247_',escape=2)
                for doi_info in doi_infos:
                    if doi_info.has_key('a'):
                        values.append(doi_info['a'])
            ####
            else:
                values.append(bfo.fields(marctag,escape=2))

    out = []
    for value in values:
        if isinstance(value, list):
            for val in value:
                if isinstance(val, dict):
                    out.extend(val.values())
                else:
                    out.append(val)
        elif isinstance(value, dict):
            out.extend(value.values())
        else:
            out.append(value)
    
    # out = dict(zip(out, len(out)*[''])).keys()
    
    # uniquify
    noDupes = []
    [noDupes.append(i) for i in out if not noDupes.count(i)]

    return '\n'.join([create_html_tag('meta', name=name, content=value) for value in noDupes])

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
