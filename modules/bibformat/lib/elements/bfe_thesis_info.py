# -*- coding: utf-8 -*-
"""BibFormat element - Prints document host"""

from invenio.messages import gettext_set_language
from invenio.bibknowledge import get_kb_mapping

def emphasize(text, css_class):
    if css_class:
        return '<span class="%s">%s</span>' % (css_class, text)
    return text

def format(bfo, brief="no"):
    """
    Print host (Order: Name of publisher, place of publication and date of publication).
    """
    _ = gettext_set_language(bfo.lang)
    output = []
    is_epfl_thesis = bfo.field("980__a") == 'THESIS' and bfo.field("973__a") == 'EPFL'
    if not is_epfl_thesis:
        #return '(%s)' % bfo.field('260__c')
        return ''
    
    thesis_number = bfo.field('088__a')
    if brief != "yes":
        output = _("Thèse École polytechnique fédérale de Lausanne EPFL, n° %(number)s (%(year)s)")
        output %= {'number': thesis_number,
                   'year': bfo.field('920__b')}
    else:
        return "Thèse EPFL, n° %(number)s (%(year)s)" % {'number': thesis_number,
                                                         'year': bfo.field('920__b')}
        
    output += '<br />'
    hierarchy = []
    if bfo.field('918__d'):
        hierarchy.append(get_kb_mapping(kb_name='doctoral-fre', key=bfo.field('918__d')))
    
    if bfo.field('918__b'):
        hierarchy.append(get_kb_mapping(kb_name='section-fre', key=bfo.field('918__b')))
    
    if bfo.field('918__a'):
        hierarchy.append(get_kb_mapping(kb_name='school-fre', key=bfo.field('918__a')))
    
    if bfo.field('918__c'):
        hierarchy.append(get_kb_mapping(kb_name='institute-fre', key=bfo.field('918__c')))
    
    if bfo.fields('919__a'):
        hierarchy.extend([get_kb_mapping(kb_name='theses-units-fre', key=unit) for unit in bfo.fields('919__a')])
    
    if bfo.field('502__a'):
        hierarchy.append({'value':  'Jury: ' + bfo.field('502__a')})
    
    output += '<br />'.join([elem['value'] for elem in hierarchy if elem])
    return output
        

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0

