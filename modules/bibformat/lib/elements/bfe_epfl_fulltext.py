# -*- coding: utf-8 -*-

"""
BibFormat element - Prints links to  fulltext
"""
from urlparse import urlparse
from os.path import basename
import urllib

from invenio.bibdocfile import BibRecDocs, file_strip_ext
from invenio.messages import gettext_set_language
from invenio.config import CFG_SITE_URL
from invenio.access_control_engine import acc_authorize_action



traditional = [
    (1024 ** 5, 'P'),
    (1024 ** 4, 'T'), 
    (1024 ** 3, 'G'), 
    (1024 ** 2, 'M'), 
    (1024 ** 1, 'K'),
    (1024 ** 0, 'B'),
    ]

alternative = [
    (1024 ** 5, ' PiB'),
    (1024 ** 4, ' TiB'), 
    (1024 ** 3, ' GiB'), 
    (1024 ** 2, ' MiB'), 
    (1024 ** 1, ' KiB'),
    (1024 ** 0, (' byte', ' bytes')),
    ]


def size_to_string(bytes, system=alternative):
    """Human-readable file size."""
    for factor, suffix in system:
        if bytes >= factor:
            break
    amount = int(bytes/factor)
    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple
    return str(amount) + suffix

def test():
    params = {'fmt': 'order', 
              'nr': 3906,
              'title': "Bose-Einstein condensation of microcavity polaritons",
              'year': 2007,
              'author': "Sarchi, Davide",
              'infoscience_id': 141282,
              'fulltext_name': 'EPFL_TH3906.pdf'}
    return urllib.urlencode(params)


def thesis_link(bfo):
    thesis_id = bfo.field('088__a', escape=2)
    thesis_title = bfo.field('245__a', escape=2)
    thesis_year = bfo.field('260__c', escape=2)
    thesis_author = bfo.field('700__a', escape=2)
    fulltext_name = 'n/a'
    for url in bfo.fields("8564_u"):
        (dummy, host, path, dummy, params, dummy) = urlparse(url)
        filename = urllib.unquote(basename(path))
        if filename.startswith('EPFL_TH'):
            fulltext_name = filename
            break
        
    params = {'fmt': 'order', 
              'nr': thesis_id,
              'title': thesis_title,
              'year': thesis_year,
              'author': thesis_author,
              'infoscience_id': bfo.recID,}
              #'fulltext_name': fulltext_name}
    
    encoded = urllib.urlencode(params)
    if bfo.lang == 'fr':
        return "http://library.epfl.ch/theses/?%s" % encoded
    else: 
        return "http://library.epfl.ch/en/theses/?%s" % encoded
    
def get_files(bfo):
    """
    Returns the files available for the given record.
    Returned structure is a tuple (parsed_urls, old_versions, additionals):

    """
    _ = gettext_set_language(bfo.lang)
    try:
        bibarchive = BibRecDocs(bfo.recID)
    except ValueError:
        # sometimes recID is no an integer...
        # so don't print anything if this is the case
        return ([], [], [])
    
    main_documents = []
    additional_documents = []
    external_urls = []
    
    user_info = bfo.user_info
    
    # before verifing access, assert that the user has a remote_ip and it is not
    # an internal call
    remote_ip = user_info.get('remote_ip', '')    
    is_thesis = bfo.field("980__a") == 'THESIS' and bfo.field("973__a") == 'EPFL'
    is_published = bfo.field("973__s") == 'PUBLISHED'
    
    # Parse URLs
    urls = bfo.fields("8564_")
    for complete_url in urls:
        if not complete_url.has_key('u'):
            continue
        
        #remove icons
        if complete_url.has_key('x') and complete_url['x'].lower() == 'icon':
            continue
        
        url = complete_url['u']
        (dummy, host, path, dummy, params, dummy) = urlparse(url)
        filename = urllib.unquote(basename(path))
        name = file_strip_ext(filename)
        format = filename[len(name):]
        if format.startswith('.'):
            format = format[1:]
        
        if not url.startswith(CFG_SITE_URL) and not complete_url.get('i'): # Not a bibdoc?
            descr = complete_url.get('z', 'URL') 
            external_urls.append((url, descr, format, 0))
        
        else: # It's a bibdoc!
            if complete_url.get('i') == 'EXTERNAL':
                filename = complete_url.get('z') or basename(complete_url['u'])
                if is_thesis and complete_url.get('x') == 'RESTRICTED':
                    if not complete_url.get('z'):
                        filename = _("Fulltext")
                    if not remote_ip:
                        # no real access
                        main_documents.append((thesis_link(bfo), filename, basename(complete_url['u']).split('.')[-1], 0))
                        continue
                    
                    if acc_authorize_action(bfo.user_info, 'viewrestrdoc', status='RESTRICTED')[0] == 1:
                        # no real access
                        main_documents.append((thesis_link(bfo), filename, basename(complete_url['u']).split('.')[-1], 0))
                        continue
                
                is_sar = 'SAR' in bfo.fields('909C0p')
                if is_sar:
                    main_documents.append((url, _("Get the whole digitalized project"), '', 0))
                    continue
                
                
                main_documents.append((complete_url['u'], filename,
                                       basename(complete_url['u']).split('.')[-1], 0))
            else:
                # Internal
                for doc in bibarchive.list_bibdocs():
                    size = doc.get_total_size_latest_version()
                    descr = doc.get_description(format)
                    
                    if True in [f.fullname.startswith(filename) for f in doc.list_all_files()]:
                        if doc.status and doc.status.lower() == 'icon':
                            continue
                        restriction = doc.list_latest_files()[0].status
                        
                        #no ip = no access, only show the public files
                        if not remote_ip:
                            if restriction not in ('LAB', 'RESTRICTED', 'PRIVATE', 'DELETED'):
                                if doc.get_type().lower() == 'main' :
                                    if not descr or descr.lower() == 'n/a':
                                        descr = name
                                        if is_thesis:
                                            descr = _("Fulltext")
                                    if not url in [m_url for (m_url, m_descr, m_format, m_size) in main_documents]:
                                        main_documents.append((url, descr, format, size))
                                else:
                                    if not descr or descr.lower() == 'n/a':
                                        descr = name
                                    if not url in [m_url for (m_url, junk, junk, junk) in additional_documents]:
                                        additional_documents.append((url, descr, format, size))
                            continue               
                        
                        #try:
                        if doc.list_latest_files()[0].is_restricted(bfo.user_info)[0] == 1:
                            continue
                        #except:
                        #   restricted = 0
                        
                        if doc.get_type().lower() == 'main' :
                            if not descr or descr.lower() == 'n/a':
                                descr = name
                            if is_thesis:
                                if restriction == 'RESTRICTED':
                                    descr = _("EPFL intranet: Fulltext")
                                else:
                                    descr = "Texte intégral / Full text"
                            if not url in [m_url for (m_url, m_descr, m_format, m_size) in main_documents]:
                                main_documents.append((url, descr, format, size))
                        
                        else:
                            if not descr or descr.lower() == 'n/a':
                                descr = name
                            if is_thesis and restriction == 'RESTRICTED':
                                descr = _("EPFL intranet: %s") % descr
                            if not url in [m_url for (m_url, junk, junk, junk) in additional_documents]:
                                additional_documents.append((url, descr, format, size))    
    if is_thesis and not main_documents and is_published:
        main_documents.append((thesis_link(bfo), _("Order free pdf"), 'pdf', 0))
    return (main_documents, additional_documents, external_urls)


def format_element(bfo, style, display_fulltext="yes", display_url="no", display_replacement_text='yes'):
    """
    This is the format for formatting fulltext links in the mini panel.
    @param separator: the separator between urls.
    @param style: CSS class of the link
    @param show_icons: if 'yes', print icons for fulltexts
    @param focus_on_main_file: if 'yes' and a doctype 'Main' is found,
    prominently display this doctype. In that case other doctypes are
    summarized with a link to the Files tab, named"Additional files".
    """
    _ = gettext_set_language(bfo.lang)
    out = """
            <ul %(style)s>
              %(fulltexts)s
            </ul>"""

    # Retrieve files
    (main_documents, additional_documents, external_documents) = get_files(bfo)
    # Prepare style
    if style != "":
        style = 'class="%s"' % style
        
    tmpl = '<li><a href="%(url)s"><div class="file-icon %(class_name)s"></div>%(filename)s (%(format)s%(size)s)</a></li>'
    tmpl_external = '<li><a href="%(url)s"><div class="file-icon %(class_name)s"></div>%(description)s</a></li>'
    
    formatted = []
    if display_fulltext.lower() == 'yes':
        for (url, name, format, size) in main_documents:
            if format.lower() == 'pdf':
                class_name = 'pdf'
            elif format.lower() in ['doc', 'docx']:
                class_name = 'doc'
            elif format.lower() in ['png', 'gif', 'jpg', 'jpeg', 'tif', 'tiff', 'bmp']:
                class_name = 'jpg'
            elif format.lower() in ['txt', 'text', 'ps']:
                class_name = 'txt'
            else:
                class_name = 'file'
            if format and size:
                formatted.append(tmpl % {'url': url, 'filename': name, 'format': format, 
                                    'size': size != 0 and ', ' + size_to_string(size) or '',
                                    'class_name': class_name })
            else:
                formatted.append(tmpl_external % {'url': url, 'description': name, 'class_name': class_name })

        
        for (url, name, format, size) in additional_documents:
            if format.lower() == 'pdf':
                class_name = 'pdf'
            elif format.lower() in ['doc', 'docx']:
                class_name = 'doc'
            elif format.lower() in ['png', 'gif', 'jpg', 'jpeg', 'tif', 'tiff', 'bmp']:
                class_name = 'jpg'
            elif format.lower() in ['txt', 'text', 'ps']:
                class_name = 'txt'
            else:
                class_name = 'file'
            if format and size:
                formatted.append(tmpl % {'url': url, 'filename': name, 'format': format, 
                                         'size': size != 0 and ', ' + size_to_string(size) or '',
                                         'class_name': class_name })
            else:
                formatted.append(tmpl_external % {'url': url, 'description': name, 'class_name': class_name })

        
        doi = bfo.field('0247_a').strip()
        if bfo.field("980__a") == 'THESIS' and bfo.field("973__a") == 'EPFL':
            if bfo.field("973__s") != 'PUBLISHED':
                formatted.append("<li>%s</li>" % _("Thesis submitted - Forthcoming publication"))
        elif doi and doi.lower() != 'n/a':
            formatted.append('<li><img style="margin-right:6px;margin-left:4px;" src="/media/img/external.png"><a href="http://dx.doi.org/%s">%s</a></li>' % (doi, _("Official version")))

    if display_url.lower() == 'yes':
        for (url, description, format, size) in external_documents:
            if url.strip():
                tmpl2 = '<li>%(description)s: <a href="%(url)s">%(url)s</a></li>'
                formatted.append(tmpl2 % {'url': url, 'description': description })
    
    if not len(formatted) and display_replacement_text.lower() == 'yes':
        formatted.append('<li>%s</li>' % _("There is no available fulltext. Please contact the lab or the authors."))
    if not formatted:
        return ''
    return out % {'style': style, 'fulltexts': '\n            '.join(formatted)}
    
    
    
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
