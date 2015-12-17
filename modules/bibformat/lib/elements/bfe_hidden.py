# -*- coding: utf-8 -*-
"""BibFormat element - Prints hidden message"""

from invenio.messages import gettext_set_language

from invenio.bibformat_elements.bfe_brief_links import can_edit

from invenio.bibformat_engine import format_with_format_template

def format(bfo, logged_template='HD_EPFL_default.bft'):
    """
    Prints the collection identifier.
    Translate using given knowledge base.    
    """
    _ = gettext_set_language(bfo.lang)
    if can_edit(bfo):
        (out, errors) = format_with_format_template(logged_template, bfo)
        return out
    
    return ''
    
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
