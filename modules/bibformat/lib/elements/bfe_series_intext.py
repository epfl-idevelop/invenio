# -*- coding: utf-8 -*-
"""BibFormat element - Prints series"""


def format(bfo, css_class='infoscience_serie'):
    """ Prints the series field of a record. """
    allseries = bfo.fields('440__')
    if len(allseries) > 0:
        series = allseries[0]
        name = series.get('a')
        volume = series.get('v')
        if name and name.strip():
            out = []
            out.append(name.strip())
            if volume:
                out.append(volume.strip())
            if css_class:
                return '<span class="%s">%s</span>' % (css_class, ' '.join(out))
            else:
                return ' '.join(out)
        return ''

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
