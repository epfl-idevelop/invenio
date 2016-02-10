# -*- coding: utf-8 -*-

"""BibFormat element - Prints authors information

Author 1, Affiliation, [link to people], find accreditations, find publications

Accreditations:
    http://accred.epfl.ch/accred/accreds.pl/viewpers?name=favre (find in accreditations)
    http://accred.epfl.ch/accred/accreds.pl/viewpers?thescip=128933 (view accreditations)


"""
from cgi import escape
from urllib import quote, urlencode

from invenio.config import CFG_SITE_URL
from invenio.messages import gettext_set_language
from invenio import bibformat_utils

from Infoscience.Names import InfoscienceName


def link_accred(author, ln):
    _ = gettext_set_language(ln)
    sciper = author.get('g', None)
    template = """
    <div class="button administration">
      <a href="%s" target="_blank">
        <button class="icon"></button>
        <span class="label">%s</span>
      </a>
    </div>
    """
    if sciper:
        url = 'http://accred.epfl.ch/accred/accreds.pl/viewpers?thescip=%s' % sciper
        return template % (url, _("View accreditations"))
    else:
        name = author.get('a').split(',')[0]
        url = 'http://accred.epfl.ch/accred/accreds.pl/viewpers?name=%s' % name
        return template % (url, _("Lookup in accred"))

def link_people(author, ln):
    _ = gettext_set_language(ln)
    sciper = author.get('g', None)
    template = """
    <div class="button contact">
      <a href="%s" target="_blank">
        <button class="icon"></button>
        <span class="label">%s</span>
      </a>
    </div>
    """
    if sciper:
        url = 'http://people.epfl.ch/%s' % sciper
        return template % (url, _("People profile"))
    
def link_affiliations(author, ln):
    affiliation = author.get('u', None)
    template = '<a href="%s" target="_blank">%s</a>'
    if affiliation:
        params = urlencode({'p': "700__u:'%s'" % affiliation, 'ln': ln})
        url = 'http://infoscience.epfl.ch/search?%s' % params
        return template % (url, affiliation)

def link_publications(author, ln):
    _ = gettext_set_language(ln)
    name = author.get('a', None)
    template = """
    <div class="button multiple">
      <a href="%s" target="_blank">
        <button class="icon"></button>
        <span class="label">%s</span>
      </a>
    </div>
    """
    params = urlencode({'p': name, 'f': 'author', 'ln': ln})
    url = 'http://infoscience.epfl.ch/search?%s' % params
    return template % (url, _("Find publications"))

def format_element(bfo):
    """
    Prints the list of authors of a record.
    """
    _ = gettext_set_language(bfo.lang)    # load the right message language
    
    output = []
    
    all_authors = []
    authors_1 = bfo.fields('100__', escape=3)
    authors_2 = bfo.fields('700__', escape=3)

    all_authors.extend(authors_1)
    all_authors.extend(authors_2)
    
    for author in all_authors:
        title = '<h4>%s</h4>' % author['a']
        
        buttons = []
        affiliation = link_affiliations(author, bfo.lang)
        if affiliation:
            title += '<em>' + affiliation + '</em>'
        
        people = link_people(author, bfo.lang)
        if people:
            buttons.append(people)
        
        buttons.append(link_accred(author, bfo.lang))
        buttons.append(link_publications(author, bfo.lang))
        output.append(title + '<div>' + '\n'.join(buttons) + '</div><div class="clear"></div>' )
        
    return '\n'.join(['<div style="margin-bottom: 1em;">%s</div>' % printable for printable in output])   


                                                      
                                                    
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
