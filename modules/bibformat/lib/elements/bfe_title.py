"""BibFormat element - Prints titles
"""
import cgi

from invenio import bibformat_utils
from invenio.bibdocfile import BibRecDocs
from invenio.config import CFG_SITE_URL

def add_link_to_fulltext(bfo, text):
    """
    Creates a link to fulltext on given text. 
    """
    documents = BibRecDocs(bfo.recID)
    
    # assert we have some files
    if documents and len(documents.bibdocs) == 0:
        return text
    
    # check visibility
    visible_list = []
    
    for doc in documents.bibdocs:
        files = doc.list_latest_files()
        if len(files):
            #try:
            fulltext = files[0]
            if fulltext.status in  ['', 'PUBLIC']:
                visible_list.append(fulltext)
            #except IndexError:
            #    return        
            
    # build url
    if len(visible_list) == 0:
        return text
    elif len(visible_list) == 1:
        #only one, return a direct url to the last version
        return '<a href ="%s">%s</a>' % (visible_list[0].fullurl, text)
    else:
        return '<a href ="%s/record/%s/files">%s</a>' % (CFG_SITE_URL, bfo.recID, text)

def format_element(bfo, separator=" ", highlight='no', latex_to_html='no', link_to_fulltext='no', punctuation = ''):
    """
    Prints the titles of a record.

    @param separator: separator between the different titles
    @param highlight: highlights the words corresponding to search query if set to 'yes'
    @param latex_to_html: if 'yes', interpret as LaTeX title
    @param link_to_fulltext: if 'yes', link title to fulltext if available.
    @param punctuation: add this char if the title don't already end with one
    """
    titles = []

    title = bfo.field('245__a')
    title_remainder = bfo.field('245__b')
    edition_statement = bfo.field('250__a')
    title_tome = bfo.field('245__n')
    title_part = bfo.field('245__p')
    
    #start with standard number if given
    standard_number = bfo.field('740__a')
    
    if len(standard_number) > 0:
        standard_number += ' - '
        titles.append(standard_number)

    if len(title) > 0:
        if title_remainder:
            title += ': ' + title_remainder
        if len(title_tome) > 0:
            title += ", " + title_tome
        if len(title_part) > 0:
            title += ": " + title_part
        titles.append( title )

    title = bfo.field('246__a')
    if len(title) > 0:
        titles.append( title )

    title = bfo.field('246__b')
    if len(title) > 0:
        titles.append( title )

    title = bfo.field('246_1a')
    if len(title) > 0:
        titles.append( title )

    titles = [cgi.escape(x) for x in titles]

    if highlight == 'yes':
        titles = [bibformat_utils.highlight(x, bfo.search_pattern) for x in titles]
    
    if len(edition_statement) > 0:
        out = separator.join(titles) + "; " + edition_statement
    else:
        out = separator.join(titles)
    
    if latex_to_html == 'yes':
        out = bibformat_utils.latex_to_html(out)
    
    if link_to_fulltext == 'yes':
        out = add_link_to_fulltext(bfo, out) 
        
    # add a , at the  end if not already
    if out and punctuation:
        if out[-1] not in [',', '.', '!', '?', ';']:
            out.append(punctuation)
    
    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0