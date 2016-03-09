# -*- coding: utf-8 -*-
"""BibFormat element - Prints link to lab"""

from invenio.messages import gettext_set_language

def format(bfo, kb_name, kb_url):
    """
    Prints the contact informations.
    Translate using given knowledge base.
    
    @param kb_name a knowledge base use to translate the lab identifier
    @param kb_url a knowledge base use to translate the lab identifier
    """ 
    lab_identifiers = bfo.fields("909C0p", escape=2)
    out = []
    for lab in lab_identifiers:
        lab_name = bfo.kb(kb_name, lab)
        lab_url = bfo.kb(kb_url, lab)
        if lab_url:
            out.append('<a href="%s">%s</a>' % (lab_url, lab_name))
        else:
            out.append('%s' % lab_name)

    # Add the TTO if we have a patent
    is_tto = False

    external_ids = bfo.fields('035__a')

    for field in external_ids:
        if 'TTO' in field:
            is_tto = True

    if bfo.field('980__a') == 'PATENT' and is_tto:
        out.append('<a href="http://tto.epfl.ch/">Technology Transfer Office</a>')

    return ''.join(['<li>%s</li>' % elem for elem in out])

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
