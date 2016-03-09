# -*- coding: utf-8 -*-
"""BibFormat element - Prints link to EPFL authors"""

from invenio.messages import gettext_set_language

def format(bfo, ):
    """
    Prints the contact informations.
    Translate using given knowledge base.
    
    TODO USE Knowledge base!!
    
    """ 
    authors = bfo.fields("700__", escape=2)
    out = []
    for author in authors:
        name = author.get('a')
        sciper = author.get('g')
        if sciper:
            out.append('<a href="http://people.epfl.ch/%s">%s</a>' % (sciper, name))
    return ''.join(['<li>%s</li>' % elem for elem in out])

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0