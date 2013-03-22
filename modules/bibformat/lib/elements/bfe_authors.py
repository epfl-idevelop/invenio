# -*- coding: utf-8 -*-

"""BibFormat element - Prints authors"""
from cgi import escape
from urllib import quote

from invenio.config import CFG_SITE_URL
from invenio.messages import gettext_set_language
from invenio import bibformat_utils

from Infoscience.Names import InfoscienceName


def format_element(bfo, limit, separator='; ',
           extension='[...]',
           print_links="yes",
           print_affiliations='no',
           affiliation_prefix = ' (',
           affiliation_suffix = ')',
           interactive="no",
           highlight="no"):
    """
    Prints the list of authors of a record.

    @param limit: the maximum number of authors to display
    @param separator: the separator between authors.
    @param extension: a text printed if more authors than 'limit' exist
    @param print_links: if yes, prints the authors as HTML link to their publications
    @param print_affiliations: if yes, make each author name followed by its affiliation
    @param affiliation_prefix: prefix printed before each affiliation
    @param affiliation_suffix: suffix printed after each affiliation
    @param interactive: if yes, enable user to show/hide authors when there are too many (html + javascript)
    @param highlight: highlights authors corresponding to search query if set to 'yes'
    """
    _ = gettext_set_language(bfo.lang)    # load the right message language
    
    output = []
    
    all_authors = []
    authors_1 = bfo.fields('100__')
    authors_2 = bfo.fields('700__')

    all_authors.extend(authors_1)
    all_authors.extend(authors_2)

    roles = {}
    for author in all_authors:
        if author.has_key('a') and author['a'].strip():
            role = 'author'
            if author.has_key('e') and author['e'].strip():
                if 'ed' in author['e'].lower():
                    role = 'editor'
                elif 'trad' in author['e'].lower():
                    role = 'translator'
                elif 'dir' in author['e'].lower():
                    role = 'director'
            if roles.has_key(role):
                roles[role].append(author)
            else:
                roles[role] = [author]
    
    if 'author' in roles.keys():
        output.append(render_authors(bfo, roles['author'], limit, separator, 
                                     extension, print_links, print_affiliations, 
                                     affiliation_prefix, affiliation_suffix, 
                                     interactive, highlight, ""))
    corporates = bfo.fields('710__a')
    if len(corporates):
        output.append(render_corporates(bfo, corporates, separator, print_links))

    if 'editor' in roles.keys():
        if len(roles['editor']) > 1:
            prefix = _("Editors")
        else:
            prefix = _("Editor")
            
        output.append(render_authors(bfo, roles['editor'], limit, separator, 
                                 extension, print_links, print_affiliations, 
                                 affiliation_prefix, affiliation_suffix, 
                                 interactive, highlight, 
                                 prefix + ": ")
                         )
        
    if 'translator' in roles.keys():
        output.append(render_authors(bfo, roles['translator'], limit, separator, 
                                     extension, print_links, print_affiliations, 
                                     affiliation_prefix, affiliation_suffix, 
                                     interactive, highlight, 
                                     len(roles['translator']) == 1 and _("Translators: ") or _("Translator: "))
                     )
    
    if 'director' in roles.keys():
        output.append(render_authors(bfo, roles['director'], limit, separator, 
                                     extension, print_links, print_affiliations, 
                                     affiliation_prefix, affiliation_suffix, 
                                     interactive, highlight, 
                                     len(roles['director']) == 1 and _("Advisor: ") or _("Advisors: "))
                     )

            
    if len(output) == 0:
        return ''
    
    return '<br />'.join(output)

def render_authors(bfo, authors_list, limit, separator='; ', extension='[...]',
                   print_links="yes", print_affiliations='no',
                   affiliation_prefix = ' (', affiliation_suffix = ')',
                   interactive="no", highlight="no", prefix=""):
    
    _ = gettext_set_language(bfo.lang)
    nb_authors = len(authors_list)
    
    for author in authors_list:
        if highlight == 'yes':
            author['a'] = bibformat_utils.highlight(author['a'], bfo.search_pattern)
        if print_links.lower() == "yes":
            author['a'] = '<a href="%s/search?f=author&amp;p=%s&amp;ln=%s">%s</a>' % \
                          (CFG_SITE_URL, quote(author['a']), bfo.lang, escape(author['a']))
        if author.has_key('u') and print_affiliations == "yes":
            author['u'] = affiliation_prefix + author['u'] + affiliation_suffix
            author['a'] = author.get('a', '') + author.get('u', '')
    
    authors = [author['a'] for author in authors_list]
    if limit.isdigit() and  nb_authors > int(limit) and interactive != "yes":
        return prefix + separator.join(authors[:int(limit)]) + extension
    
    elif limit.isdigit() and nb_authors > int(limit) and interactive == "yes":
        return """%s%s<br />
                  <div class="toggler"><a href="#">%s</a></div>
                  <div class="toggled" style="display:none">%s</div>""" % (prefix, 
                                                      separator.join(authors[:int(limit)]),
                                                      _("Show all %i authors") % nb_authors,
                                                      separator.join(authors[int(limit):]))
    else:
        return prefix + separator.join(authors)
                                                      
                                                    
def render_corporates(bfo, corporate_list, separator, print_links):
    out = []
    for corporate in corporate_list:
        if  print_links.lower() == "yes":
            out.append('<a href="%s/search?f=710__a&amp;p=%s&amp;ln=%s">%s</a>' % \
                          (CFG_SITE_URL, quote(corporate), bfo.lang, escape(corporate)))
        else:
            out.append(coporate)
    return separator.join(out)


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0