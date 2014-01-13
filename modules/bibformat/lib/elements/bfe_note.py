# -*- coding: utf-8 -*-
"""BibFormat element - Prints note"""


def format(bfo):
    """
    Print note.

    """
    output = ''
    for note in bfo.fields('500__a'):
        if note.strip():
            output += '<p>%s</p>' % note.strip()
    
    return output


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
        

