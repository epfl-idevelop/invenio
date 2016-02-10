# -*- coding: utf-8 -*-
##
## $Id: bfe_imprint.py,v 1.6 2007/02/14 18:32:17 tibor Exp $
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
"""BibFormat element - Prints editor information"""

from invenio.messages import gettext_set_language

def emphasize(text):
    return '<em>%s</em>' % text

def format(bfo, style_status='', style_text='', separator=', '):
    """
    Print host (Order: Name of publisher, place of publication and date of publication).

    """
    output = []    
    if bfo.field('260__b') and bfo.field('260__b').strip():
        output.append(bfo.field('260__b', escape=3))
    if bfo.field('260__a') and bfo.field('260__a').strip():
        output.append(bfo.field('260__a', escape=3))
#    if bfo.field('260__c') and bfo.field('260__c').strip():
#        output.append(bfo.field('260__c'))                
    return separator.join(output)
        

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0

