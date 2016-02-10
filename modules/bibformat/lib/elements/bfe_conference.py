"""BibFormat element - Prints conference informations"""
from invenio.messages import gettext_set_language

def format(bfo, separator=', ', year="yes"):
    """
    Print host (Order: Name of publisher, place of publication and date of publication).

    """
    output = []
    date = False
    # name
    if bfo.field('7112_a') and bfo.field('7112_a').strip():
        output.append(bfo.field('7112_a', escape=3).strip())
    
    # location
    if bfo.field('7112_c') and bfo.field('7112_c').strip():
        output.append(bfo.field('7112_c', escape=3).strip())
    
    # date
    if year == "yes" and bfo.field('7112_d') and bfo.field('7112_d').strip():
        output.append(bfo.field('7112_d', escape=3))
    
    return separator.join(output)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0