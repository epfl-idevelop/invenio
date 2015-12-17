# -*- coding: utf-8 -*-
"""BibFormat element - Prints series"""


def format(bfo, separator=', '):
    """ Prints the series field of a record. """
    name = bfo.field('440__a').strip()
    output = []
    if name:
        output.append(name)
        volume = bfo.field('440__v')
        if volume:
            output.append('vol. ' + volume)
    return separator.join(output)