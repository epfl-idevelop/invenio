# -*- coding: utf-8 -*-
"""BibFormat element - Prints Award information"""
from datetime import datetime
def format(bfo):
    """
    Print ISBN.

    """
    output = ''
    if bfo.field('920__a') and bfo.field('920__a').strip():
        output = bfo.field('920__a').strip()            
    return output