# -*- coding: utf-8 -*-
"""BibFormat element - Prints document host"""

from invenio.messages import gettext_set_language

def emphasize(text, css_class):
    if css_class:
        return '<span class="%s">%s</span>' % (css_class, text)
    return text

def format(bfo, separator=', ', hostname_class="", display_label="no", display_identifiers="no", label_with_span="no"):
    """
    Print host (Order: Name of publisher, place of publication and date of publication).
    """
    _ = gettext_set_language(bfo.lang)
    output = []
    if bfo.field('773__p') and bfo.field('773__p', escape=2).strip():
        journal_name = bfo.field('773__p', escape=2).strip()
        if display_identifiers == 'yes':
            if bfo.field('773__x', escape=2):
                # ISSN provided
                issn = bfo.field('773__x', escape=2)
                journal_name = '%s (ISSN: <a href="http://www.sherpa.ac.uk/romeo/search.php?search=%s&jrule=ISSN">%s</a>)' % (journal_name, issn, issn)
            if bfo.field('773__z', escape=2):
                # ISBN provided
                journal_name = '%s (ISBN: %s)' % (journal_name,  bfo.field('773__z', escape=2))
    
        status = bfo.field('973__s')
        if display_label == 'yes':
            if status == 'SUBMITTED':
                output.append('<span class="field-label">' + _("Submitted to") + ':</span> ' + journal_name)
            elif status == 'ACCEPTED':
                output.append('<span class="field-label">' + _("Accepted in") + ':</span> ' + journal_name)
            else:
                output.append('<span class="field-label">' + _("Published in") + ':</span> ' + journal_name)
        else:
            if status == 'SUBMITTED':
                output.append((_("Submitted to")).lower() + ' ' + journal_name)
            elif status == 'ACCEPTED':
                output.append((_("Accepted in")).lower() + ' ' + journal_name)
            else:
                output.append(emphasize("in " + bfo.field('773__p').strip(), hostname_class))

        if bfo.field('773__v') and bfo.field('773__v').strip():
            output.append('vol.&nbsp;' + bfo.field('773__v', escape=2))
        
        if bfo.field('773__n') and bfo.field('773__n').strip():
            output.append('num.&nbsp;' + bfo.field('773__n', escape=2))
        
        if bfo.field('773__c') and bfo.field('773__c').strip():
            output.append('p.&nbsp;' + bfo.field('773__c', escape=2))
        
    return separator.join(output)
        

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0

