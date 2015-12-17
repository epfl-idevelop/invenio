"""
BibFormat element - Prints icon
"""

import re
from cgi import escape


from invenio.messages import gettext_set_language

        
def format_element(bfo, style='record-illustration', link="no", link_class=""):
    """
    display an icon using provided css class
    @style: css class to appy
    """
    _ = gettext_set_language(bfo.lang)
    if link == "yes":
        tmpl = """
            <a href="%(url)s" class="%(link_class)s"><img src="%(url)s" class="%(style)s" alt="%(description)s" /></a>"""
    else:
        tmpl = """
            <img src="%(url)s" class="%(style)s" alt="%(description)s" />"""
    out = ''
    urls = bfo.fields("8564_")
    for complete_url in urls:
        if not complete_url.has_key('u'):
            continue
        url = complete_url['u']
        if not complete_url.has_key('x') or complete_url['x'].lower() != 'icon':
            continue
        description = complete_url.has_key('z') and complete_url['z'] or ''
        out += tmpl % {'url': url, 'link_class': link_class, 
                       'style': style, 'description': description}

    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
