# -*- coding: utf-8 -*-
"""BibFormat element - Get contacts informations from different bfe and format it, if any
This is currently used in HD_EPFL_default.bft"""

from invenio.bibformat_elements.bfe_contact_lab import format as format_element_labs
from invenio.bibformat_elements.bfe_contact_authors import format as format_element_authors

def format(bfo, kb_name, kb_url):
    full_html = ''
    full_html_labs = ''
    full_html_authors = ''

    html_wrapper = '<div class="box"><h3>Contacts</h3>%s%s</div>'

    html_labs = format_element_labs(bfo, kb_name, kb_url) or ''
    html_authors = format_element_authors(bfo) or ''

    if html_labs:
        full_html_labs = '<ul class="link-list" style="margin-bottom: 20px;">%s</ul>' % html_labs

    if html_authors:
        if bfo.lang == 'fr':
            full_html_authors = '<h4>Auteurs EPFL</h4><ul class="link-list">%s</ul>' % html_authors
        else: 
            full_html_authors = '<h4>EPFL authors</h4><ul class="link-list">%s</ul>' % html_authors

    if full_html_labs or full_html_authors:
        full_html = html_wrapper % (full_html_labs, full_html_authors)

    return full_html

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
