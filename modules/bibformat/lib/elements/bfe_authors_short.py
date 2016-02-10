"""
BibFormat element - Prints authors
"""
from urllib import quote

from Infoscience.Names import InfoscienceName

from invenio.config import CFG_SITE_URL

def __url_to_author(author):
#    if author.has_key('g') and author['g'].strip():
#        url = 'http://people.epfl.ch/%s' % author['g'].strip()
    #else:
    url = CFG_SITE_URL + '/search?f=author&amp;p='+ quote(author['a'])
    return url

def __url_to_corporate(corporate):
    url = CFG_SITE_URL + '/search?f=710__a&amp;p='+ quote(corporate)
    return url

def __link(author, url):
    return '<a href="%s">%s</a>' % (url, author)
    
def __span(author, author_class):
    if author_class:
        return '<span class="%s">%s</span>' % (author_class, author)
    return author

def format(bfo, limit=5, extension=" et al", limit_to="", print_links="no", author_class=""):
    """
    Prints the list of authors of a record.
    
    @param limit the maximum number of authors to display
    @param separator the separator between authors.
    @param extension a text printed if more authors than 'limit' exist
    @param print_links if yes, prints the authors as HTML link to their publications
    @param print_roles if yes, make each author name followed by its role
    @param role_prefix prefix printed before each role
    @param role_suffix suffix printed after each role
    @param interactive if yes, enable user to show/hide authors when there are too many (html + javascript)
    @param highlight highlights authors corresponding to search query if set to 'yes'
    """
    limit= int(limit)
    print_links = (print_links == "yes")
    
    is_part_of_something = (len(bfo.fields('773__')) > 0)
    
    output = []
    authors = bfo.fields('700__', escape=3)
    roles = {}
    for author in authors:
        if author.has_key('a') and author['a'].strip():
            role = 'author'
            if author.has_key('e') and author['e'].strip():
                if 'ed' in author['e'].lower():
                    role = 'editor'
                elif 'trad' in author['e'].lower():
                    role= 'translator'
                elif 'dir' in author['e'].lower():
                    role = 'director'
            if roles.has_key(role):
                roles[role].append((author['a'], __url_to_author(author)))
            else:
                roles[role] = [(author['a'], __url_to_author(author))]
    total_len = 0
    
    
    if 'author' in roles.keys():
        authors = roles['author']
        if len(authors) > limit:
            if len(authors[:limit]):
                output.append(render_authors(authors[:limit], print_links, author_class))
            return ', '.join(output) + extension
        else:
            total_len += len(authors)
            output.append(render_authors(authors, print_links, author_class))

    if not is_part_of_something:
        if 'editor' in roles.keys():
            editors = roles['editor']
            if total_len + len(editors) > limit:
                if len(editors[:limit - total_len]):
                    output.append(render_editors(editors[:limit - total_len], print_links, author_class))
                return ', '.join(output) + extension
            else:
                total_len += len(editors)
                output.append(render_editors(editors, print_links, author_class))

    if 'director' in roles.keys():
        directors = roles['director']
        if total_len + len(directors) > limit:
            if len(directors[:limit - total_len]):
                output.append(render_directors(directors[:limit - total_len], print_links, author_class))
            return ', '.join(output) + extension
        else:
            total_len += len(directors)
            output.append(render_directors(directors, print_links, author_class))

    if 'translator' in roles.keys():
        translators = roles['translator']
        if total_len + len(translators) > limit:
            if len(translators[:limit - total_len]):
                output.append(render_translators(translators[:limit - total_len], print_links, author_class))
            return ', '.join(output) + extension
        else:
            total_len += len(translators)
            output.append(render_translators(translators, print_links, author_class))
    
    corporates = bfo.fields('710__a', escape=3)
    if len(corporates):
        output.append(render_corporates(corporates, print_links, author_class))
    
    if len(output) == 0:
        return ''
    
    if limit_to == "author":
        return output[0]
    else:     
        return ', '.join(output)



def render_authors(authors, print_links=False, author_class=""):
    if print_links:
        auts = [__span(__link(InfoscienceName(author).ieee_render(), url), author_class) for (author, url) in authors]
    else:
        auts = [__span(InfoscienceName(author).ieee_render(), author_class) for (author, url) in authors]
    if len(auts) > 1:
        return ' and '.join([', '.join(auts[0:-1]), auts[-1]])
    else:
        return auts[0]

def render_editors(editors, print_links=False, author_class=""):
    if print_links:
        eds = [__span(__link(InfoscienceName(editor).ieee_render(), url), author_class) for (editor, url) in editors]
    else:
        eds = [__span(InfoscienceName(editor).ieee_render(), author_class) for (editor, url) in editors]
    if len(eds) > 1:
        return ' and '.join([', '.join(eds[0:-1]), eds[-1]]) + ' (Eds.)'
    else:
        return eds[0] + ' (Ed.)'
    
    
def render_translators(translators, print_links=False, author_class=""):
    if print_links:
        trans = [__span(__link(InfoscienceName(translator).ieee_render(), url), author_class) for (translator, url) in translators]
    else:
        trans = [__span(InfoscienceName(translator).ieee_render(), author_class) for (translator, url) in translators]
    if len(trans) > 1:
        return ' and '.join([', '.join(trans[0:-1]), trans[-1]]) + ' (Trans.)'
    else:
        return trans[0] + ' (Trans.)'

def render_directors(directors, print_links=False, author_class=""):
    if print_links:
        dirs = [__span(__link(InfoscienceName(director).ieee_render(), url), author_class) for (director, url) in directors]
    else:
        dirs = [__span(InfoscienceName(director).ieee_render(), author_class) for (director, url) in directors]
    if len(dirs) > 1:
        return ' and '.join([', '.join(dirs[0:-1]), dirs[-1]]) + ' (Dirs.)'
    else:
        return dirs[0] + ' (Dir.)'

def render_corporates(corporates, print_links=False, author_class=""):
    if print_links:
        corps = [__span(__link(corporate, __url_to_corporate(corporate)), author_class) for corporate in corporates]
    else:
        corps = [__span(corporate, author_class) for corporate in corporates]
    if len(corps) > 1:
        return ' and '.join([', '.join(corps[0:-1]), corps[-1]])
    else:
        return corps[0]


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
