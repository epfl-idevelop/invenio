# -*- coding: utf-8 -*-
"""BibFormat element - Prints Patent Number"""


def format(bfo):
    """
    Print ISBN.

    """
    output = ''
    if bfo.field('013__a') and bfo.field('013__a').strip():
        output = bfo.field('013__a').strip()            
    return output
        

