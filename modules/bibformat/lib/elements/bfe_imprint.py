# -*- coding: utf-8 -*-
"""BibFormat element - Prints info about publisher"""

from invenio.messages import gettext_set_language



def format(bfo, separator=', ', hostname_class="", display_label="no", display_year="no", display_identifiers="no"):
    """
    Print host (Order: Name of publisher, place of publication and date of publication).
    """
    _ = gettext_set_language(bfo.lang)
    output = ''
    year = bfo.field('260__c')
    if not year:
        return output
    publisher = bfo.field('260__b')
    if publisher:
        place = bfo.field('260__a')
        if place:
            output = '%s: %s, %s' % (place, publisher, year)
        else:
            output = '%s, %s' % (publisher, year)
    else:
        # if patent, set label to Priority Date
        if bfo.field('980__a') == 'PATENT':
            output = '<span class="field-label">%s:</span> %s' % (_("Priority date"), year)
        else:
            output = '<span class="field-label">%s:</span> %s' % (_("Publication date"), year)
    return output        

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0

