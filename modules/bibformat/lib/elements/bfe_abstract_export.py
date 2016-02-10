# -*- coding: utf-8 -*-
##
## $Id: bfe_abstract.py,v 1.14 2007/07/24 10:21:28 kaplun Exp $
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
"""BibFormat element - Prints English and French abstract.
"""

__revision__ = "$Id: bfe_abstract.py,v 1.14 2007/07/24 10:21:28 kaplun Exp $"

#import cgi
from invenio import bibformat_utils
from urllib import quote
import re

#invalid and old import
#from invenio.bibformat_config import CFG_BIBFORMAT_HAS_MIMETEX

latex_formula_re = re.compile(r'\$(.*?)\$')
def fix_latex_formulas(text):
    """Substitute every occurency of a Latex Formula with a proper image
    representing it, produce by MimeTeX."""
    text=text.replace('&amp;lt', '<')
    text=text.replace('\$', '&#36;')
    def replace(match):
        return '<img src="/cgi-bin/mimetex.cgi?%s" alt="%s" border="0" />' % (quote(r'\small ' + match.group(1)), match.group(1))
    return latex_formula_re.sub(replace, text)


def format(bfo, limit, max_chars, extension="[...] ", languages='en', latex="no"):
    """ Prints the abstract of a record in HTML. By default prints English and French versions.
    @param prefix_en a prefix for english abstract (printed only if english abstract exists)
    @param prefix_fr a prefix for french abstract (printed only if french abstract exists)
    @param limit the maximum number of sentences of the abstract to display (for each language)
    @param max_chars the maximum number of chars of the abstract to display (for each language)
    @param extension a text printed after abstracts longer than parameter 'limit'
    @param suffix_en a suffix for english abstract(printed only if english abstract exists)
    @param suffix_fr a suffix for french abstract(printed only if french abstract exists)
    @parmm contextual if 'yes' prints sentences the most relative to user search keyword (if limit < abstract)
    @param highlight if 'yes' highlights words from user search keyword
    """
    out = ''
    abstract_en = []
    abstract_fr = []
    for abstract in bfo.fields('520__', escape=3):
        lang = abstract.get('9', 'eng')
        if lang == 'eng':
            abstract_en.append(abstract.get('a', ''))
        else:
            abstract_fr.append(abstract.get('a', ''))
    
    #abstract_en = bfo.fields('520__a', escape=3)
    #abstract_en.extend(bfo.fields('520__b', escape=3))
    abstract_en = "<br />".join(abstract_en)

    #abstract_fr = bfo.fields('590__a', escape=3)
    #abstract_fr.extend(bfo.fields('590__b', escape=3))
    abstract_fr = "<br />".join(abstract_fr)

    if limit != "" and limit.isdigit() and int(limit) > 0:
        context_en = bibformat_utils.get_contextual_content(abstract_en,
                                                            bfo.search_pattern,
                                                            max_lines=int(limit))
        #FIXME add something like [...] before and after
        #contextual sentences when not at beginning/end of abstract
        #if not abstract_en.strip().startswith(context_en[0].strip()):
        #    out += '[...]'
        abstract_en = "<br/>".join(context_en)
        context_fr = bibformat_utils.get_contextual_content(abstract_fr,
                                                            bfo.search_pattern,
                                                            max_lines=int(limit))
        abstract_fr = "<br/>".join(context_fr)
    if len(abstract_en) > 0 and 'en' in languages:
        print_extension = False
        if max_chars != "" and max_chars.isdigit() and int(max_chars) < len(abstract_en):
            print_extension = True
            abstract_en = abstract_en[:int(max_chars)]
        if limit != "" and limit.isdigit():
            s_abstract = abstract_en.split(".")
            if int(limit) < len(s_abstract):
                print_extension = True
                s_abstract = s_abstract[:int(limit)]
            #for sentence in s_abstract:
            #    out += sentence + "."
            out = '.'.join(s_abstract)

            # Add final dot if needed
            if abstract_en.endswith('.'):
                out += '.'

            if print_extension:
                out += " " + extension
            
        else:
            out += abstract_en

    if len(abstract_fr) > 0 and 'fr' in languages:

        print_extension = False

        if max_chars != "" and max_chars.isdigit() and \
               int(max_chars) < len(abstract_fr):
            print_extension = True
            abstract_fr = abstract_fr[:int(max_chars)]

        if limit != "" and limit.isdigit():
            s_abstract = abstract_fr.split(".")

            if int(limit) < len(s_abstract):
                print_extension = True
                s_abstract = s_abstract[:int(limit)]

            #for sentence in s_abstract:
            #    out += sentence + "."
            out = '.'.join(s_abstract)

            # Add final dot if needed
            if abstract_fr.endswith('.'):
                out += '.'

            if print_extension:
                out += " "+ extension

        else:
            out += abstract_fr

    if latex=="yes":
        return fix_latex_formulas(out)
    else:
        return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
