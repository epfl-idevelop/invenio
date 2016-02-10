# -*- coding: utf-8 -*-
"""BibFormat element - Prints references"""
import re

from invenio.messages import gettext_set_language


def format(bfo):
    """
    Print host (Order: Name of publisher, place of publication and date of publication).

    """
    _ = gettext_set_language(bfo.lang)
    output = []
    epflid = bfo.field('037__a', escape=3).strip()
    if epflid:
        output.append(epflid)
    
    doi = bfo.field('0247_a', escape=3).strip()
    if doi:
        doi_re = re.compile(r'(10.(\d)+/(\S)+)')
        if doi_re.search(doi):
            output.append('<a href="http://dx.doi.org/%s">doi:%s</a>' % (doi, doi))
            
    # show patent search ?
    if bfo.field('013__a'):
        if bfo.lang == 'fr':
            url = "http://worldwide.espacenet.com/searchResults?compact=false&PN=%s&ST=advanced&locale=fr_EP&DB=EPODOC" % str(bfo.field('013__a'))
        else:
            url = "http://worldwide.espacenet.com/searchResults?compact=false&PN=%s&ST=advanced&locale=en_EP&DB=EPODOC" % str(bfo.field('013__a'))
        output.append('<a href="%s" target="_blank">%s</a>' % (url, _("Search for this record at the European Patent Office")))

    external = bfo.fields('035__a')
    control_nb_re = re.compile(r'(?P<id>[\w:_,.\-_/]+)\s*\((?P<cataloger>[a-z\s]+)\)', re.I)
    for ext in external:
        match = control_nb_re.match(ext)
        if match:
            extra_id = match.group('id')
            cataloger = match.group('cataloger')
        if cataloger == 'ISI':
            url = 'http://ws.isiknowledge.com/cps/openurl/service?url_ver=Z39.88-2004&amp;rft_id=info:ut/%s' % extra_id
            output.append('<a href="%s">%s</a>' % (url, _("View record in Web of Science")))
        elif cataloger == 'Scopus':
            url = 'http://www.scopus.com/scopus/openurl/link.url?ctx_ver=Z39.88-2004&amp;rfr_id=http://infoscience.epfl.ch&amp;rft_id=info:eid/%s' % extra_id
            output.append('<a href="%s">%s</a>' % (url, _("View record in Scopus")))
        elif cataloger == 'PMID':
            url = 'http://www.ncbi.nlm.nih.gov/sites/entrez?cmd=Retrieve&db=PubMed&list_uids=%s&dopt=Abstract' % extra_id
            output.append('<a href="%s">%s</a>' % (url, _("View record in PubMed")))
        elif cataloger == 'arXiv':
            url = 'http://www.arxiv.org/openurl-resolver?rft_id=%s&amp;url_ver=Z39.88-2004' % extra_id
            output.append('<a href="%s">%s</a>' % (url, _("View record in arXiv")))
        elif cataloger == 'EV':
            pass
        elif cataloger == 'SzZuIDS NEBIS':
            if bfo.lang == 'fr':
                url = 'http://library.epfl.ch/nebis-redir/?record=%s' % extra_id
            else:
                url = 'http://library.epfl.ch/en/nebis-redir/?record=%s' % extra_id
            
            output.append('<a href="%s">%s</a>' % (url, _("Print copy in library catalog")))
        
        
    return ''.join(['<li>%s</li>' % elem for elem in output])

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
