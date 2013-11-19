# -*- coding: utf-8 -*-
# pylint: disable=C0301
"""
EPFL templates.
Websearch handles search pages and detailed record pages. These templates are also used by webcoll CLI
"""

import cgi, re, math
from urllib import quote, FancyURLopener

from invenio.config import \
     CFG_WEBSEARCH_ADVANCEDSEARCH_PATTERN_BOX_WIDTH, \
     CFG_WEBSEARCH_SPLIT_BY_COLLECTION, \
     CFG_WEBSEARCH_DEF_RECORDS_IN_GROUPS, \
     CFG_BIBRANK_SHOW_READING_STATS, \
     CFG_BIBRANK_SHOW_DOWNLOAD_STATS, \
     CFG_BIBRANK_SHOW_DOWNLOAD_GRAPHS, \
     CFG_SITE_LANG, \
     CFG_SITE_NAME, \
     CFG_SITE_NAME_INTL, \
     CFG_SITE_URL, \
     CFG_INSPIRE_SITE, \
     CFG_WEBSEARCH_DEFAULT_SEARCH_INTERFACE, \
     CFG_WEBSEARCH_ENABLED_SEARCH_INTERFACES, \
     CFG_WEBSEARCH_MAX_RECORDS_IN_GROUPS, \
     CFG_BIBINDEX_CHARS_PUNCTUATION
from invenio.dbquery import run_sql
from invenio.messages import gettext_set_language
from invenio.urlutils import make_canonical_urlargd, drop_default_urlargd, create_html_link, create_url
from invenio.intbitset import intbitset


import invenio.websearch_templates

_RE_PUNCTUATION = re.compile(CFG_BIBINDEX_CHARS_PUNCTUATION)
_RE_SPACES = re.compile(r"\s+")

def get_fieldvalues(recID, tag):
    """Return list of field values for field TAG inside record RECID.
       FIXME: should be imported commonly for search_engine too."""
    out = []
    if tag == "001___":
        # we have asked for recID that is not stored in bibXXx tables
        out.append(str(recID))
    else:
        # we are going to look inside bibXXx tables
        digit = tag[0:2]
        bx = "bib%sx" % digit
        bibx = "bibrec_bib%sx" % digit
        query = "SELECT bx.value FROM %s AS bx, %s AS bibx WHERE bibx.id_bibrec='%s' AND bx.id=bibx.id_bibxxx AND bx.tag LIKE '%s'" \
                "ORDER BY bibx.field_number, bx.tag ASC" % (bx, bibx, recID, tag)
        res = run_sql(query)
        for row in res:
            out.append(row[0])
    return out


class Template(invenio.websearch_templates.Template):

    # Type of the allowed parameters for the web interface for search results
    search_results_default_urlargd = {
        'cc': (str, CFG_SITE_NAME),
        'c': (list, []),
        'p': (str, ""), 'f': (str, ""),
        'rg': (int, CFG_WEBSEARCH_DEF_RECORDS_IN_GROUPS),
        'sf': (str, ""),
        'so': (str, "d"),
        'sp': (str, ""),
        'rm': (str, ""),
        'of': (str, "hb"),
        'ot': (list, []),
        'aas': (int, CFG_WEBSEARCH_DEFAULT_SEARCH_INTERFACE),
        'as': (int, CFG_WEBSEARCH_DEFAULT_SEARCH_INTERFACE),
        'p1': (str, ""), 'f1': (str, ""), 'm1': (str, ""), 'op1':(str, ""),
        'p2': (str, ""), 'f2': (str, ""), 'm2': (str, ""), 'op2':(str, ""),
        'p3': (str, ""), 'f3': (str, ""), 'm3': (str, ""),
        'sc': (int, 0),
        'jrec': (int, 0),
        'recid': (int, -1), 'recidb': (int, -1), 'sysno': (str, ""),
        'id': (int, -1), 'idb': (int, -1), 'sysnb': (str, ""),
        'action': (str, "search"),
        'action_search': (str, ""),
        'action_browse': (str, ""),
        'd1': (str, ""),
        'd1y': (int, 0), 'd1m': (int, 0), 'd1d': (int, 0),
        'd2': (str, ""),
        'd2y': (int, 0), 'd2m': (int, 0), 'd2d': (int, 0),
        'dt': (str, ""),
        'ap': (int, 1),
        'verbose': (int, 0),
        'ec': (list, []),
        'ext': (list, []),
        }

    # ...and for search interfaces
    search_interface_default_urlargd = {
        'aas': (int, CFG_WEBSEARCH_DEFAULT_SEARCH_INTERFACE),
        'as': (int, CFG_WEBSEARCH_DEFAULT_SEARCH_INTERFACE),
        'verbose': (int, 0)}

    def build_search_url(self, known_parameters={}, **kargs):
        """ Helper for generating a canonical search
        url. 'known_parameters' is the list of query parameters you
        inherit from your current query. You can then pass keyword
        arguments to modify this query.

           build_search_url(known_parameters, of="xm")

        The generated URL is absolute.
        """

        parameters = {}
        parameters.update(known_parameters)
        parameters.update(kargs)

        # Now, we only have the arguments which have _not_ their default value
        parameters = drop_default_urlargd(parameters, self.search_results_default_urlargd)

        # Treat `as' argument specially:
        if parameters.has_key('aas'):
            parameters['as'] = parameters['aas']
            del parameters['aas']

        # Asking for a recid? Return a /record/<recid> URL
        if 'recid' in parameters:
            target = "/record/%s" % parameters['recid']
            del parameters['recid']
            target += make_canonical_urlargd(parameters, self.search_results_default_urlargd)
            return target

        return "/search%s" % make_canonical_urlargd(parameters, self.search_results_default_urlargd)
    
    def build_search_interface_url(self, known_parameters={}, **kargs):
        """ Helper for generating a canonical search interface URL."""

        parameters = {}
        parameters.update(known_parameters)
        parameters.update(kargs)
        
        if parameters.get('cc'):
            c = None
        else:
            c = parameters['c']
            del parameters['c']

        # Now, we only have the arguments which have _not_ their default value
        parameters = drop_default_urlargd(parameters, self.search_results_default_urlargd)

        # Treat `as' argument specially:
        if parameters.has_key('aas'):
            parameters['as'] = parameters['aas']
            del parameters['aas']

        if c and c != CFG_SITE_NAME:
            base = '/collection/' + quote(c)
        elif parameters:
            base = '/search'
        else: 
            base = ''
        return create_url(base, parameters)
    
    def tmpl_record_page_header_content(self, req, recid, ln):
        """ Provide extra information in the header of /record pages """
        _ = gettext_set_language(ln)
        title = get_fieldvalues(recid, "245__a")
        if title:
            title = cgi.escape(title[0])
        else:
            title = _("Record") + ' #%d' % recid

        keywords = ', '.join(get_fieldvalues(recid, "6531_a"))
        description = ' '.join(get_fieldvalues(recid, "520__a"))
        description += "\n"
        description += '; '.join(get_fieldvalues(recid, "100__a") + get_fieldvalues(recid, "700__a"))

        return [cgi.escape(x, True) for x in (title, description, keywords)]

    def tmpl_navtrail_links(self, aas, ln, dads):
        """
        EPFL
        Creates the navigation bar at top of each search page (*Home > Root collection > subcollection > ...*)
        Parameters:

          - 'aas' *int* - Should we display an advanced search box?
          - 'ln' *string* - The language to display
          - 'separator' *string* - The separator between two consecutive collections
          - 'dads' *list* - A list of parent links, eachone being a dictionary of ('name', 'longname')
        """
        links = []
        for url, name in dads:
            args = {'c': url, 'as': aas, 'ln': ln}
            links.append(create_html_link(self.build_search_interface_url(**args), {}, url.split('/')[-1] ))
        out = []
        if len(links):
            out += ['<li>%s</li>' % link for link in links]
        return ''.join(out)

    def tmpl_webcoll_body(self, ln, collection, te_portalbox,
                          searchfor, np_portalbox, narrowsearch,
                          focuson, instantbrowse, ne_portalbox):

        """
        EPFL
        Creates the body of the main search page.
        Parameters:
          - 'ln' *string* - language of the page being generated
          - 'collection' - collection id of the page being generated
          - 'te_portalbox' *string* - The HTML code for the portalbox on top of search
          - 'searchfor' *string* - The HTML code for the search for box
          - 'np_portalbox' *string* - The HTML code for the portalbox on bottom of search
          - 'narrowsearch' *string* - The HTML code for the search categories (left bottom of page)
          - 'focuson' *string* - The HTML code for the "focuson" categories (right bottom of page)
          - 'ne_portalbox' *string* - The HTML code for the bottom of the page
        """
        from invenio.websearch_webcoll import Collection
        _ = gettext_set_language(ln)
        
        if collection == CFG_SITE_NAME:
            return self.tmpl_homepage(searchfor, ln)
        
        c = Collection(collection)
        if narrowsearch:
            right_col = """          
          <ul class="tree">
%(narrowsearch)s
%(focuson)s
          </ul>""" % {'narrowsearch': narrowsearch, 'focuson': focuson,}
        else:
            right_col = """        
        <div class="box box-flat-panel home-navpanel local-color">
          <h3>%(title)s</h3>
          <ul>
            <li><a href="%(guidelines_url)s">%(guidelines_label)s</a></li>
            <li><a href="%(fns1_url)s">%(fns1_label)s</a></li>
            <li><a href="%(fns2_url)s">%(fns2_label)s</a></li>
            <li><a href="%(erc_url)s">%(erc_label)s</a></li>
          </ul>
        </div>
      </div>""" % { 
    'title': _("Infoscience, EPFL's scientific publications"),
                       
    'guidelines_url': ln == 'en' and 'http://polylex.epfl.ch/files/content/sites/polylex/files/recueil_pdf/ENG/3.3.2_principe_integrite_recherche_an.pdf' or 
                                     'http://polylex.epfl.ch/files/content/sites/polylex/files/recueil_pdf/3.3.2_principe_integrite_recherche_fr.pdf',
    'guidelines_label': _("EPFL Directive for Research Integrity"),
                       
    'fns1_url': ln == 'en' and 'http://www.snf.ch/SiteCollectionDocuments/allg_reglement_valorisierung_e.pdf' or 
                               'http://www.snf.ch/SiteCollectionDocuments/dos_OA_Weisung_f.pdf',
    'fns1_label': _("SNSF regulations on information, valorisation and rights to research results"),
                       
                       
    'fns2_url': ln == 'en' and 'http://www.snf.ch/SiteCollectionDocuments/Dossiers/dos_OA_regelung_auf_einen_blick_e.pdf' or 
                               'http://www.snf.ch/SiteCollectionDocuments/Dossiers/dos_OA_regelung_auf_einen_blick_f.pdf',
    'fns2_label': _("Overview of SNSF Guidelines on Open Access"),             


    'erc_url': 'http://erc.europa.eu/sites/default/files/press_release/files/open_access_policy_researchers_funded_ERC.pdf',
    'erc_label': _("Open Access Guidelines for researchers funded by the ERC"),             

}
        body = """
        <div id="tools">
          <div class="button feed">
            <a href="%(feed)s">
              <button class="icon"></button>
              <span class="label">%(feed_label)s</span>
            </a>
          </div>      
        </div>
        <div id="content" class="content">
          <h1 class="h2 no-bottom-margin">%(title)s</h1>
%(te_portalbox)s
%(searchfor)s
%(np_portalbox)s
          <h3>%(instant_label)s</h3>
%(instantbrowse)s
%(ne_portalbox)s
        </div>
        <div class="right-col">
%(right_col)s
        </div>
        <div class="clear"></div>""" % \
      {'title': c.get_name(ln=ln),
        'te_portalbox': te_portalbox,
        'searchfor': searchfor,
        'np_portalbox': np_portalbox,
        'ne_portalbox': ne_portalbox,
        'right_col': right_col,
        'instantbrowse': instantbrowse,
        'instant_label': _('Latest additions'),
        'feed': self.build_rss_url({'c': collection, 'ln': ln}),
        'feed_label': 'RSS',
      }
        return body

    def tmpl_homepage(self, searchfor, ln):
        """
        EPFL: infoscience's homepage
        """
        from invenio.websearch_webcoll import Collection
        research = Collection('Infoscience/Research')
        resource = Collection('Infoscience/Resource')

        _ = gettext_set_language(ln)
        try:
            f = FancyURLopener().open('http://actu.epfl.ch/webservice?channel=79&lang=%s&template=4' % ln)
            news_feed = f.read()
        except:
            news_feed = ''
        
        body = """
      <div id="tools">
          <div class="button feed">
            <a href="%(feed)s">
              <button class="icon"></button>
              <span class="label">%(feed_label)s</span>
            </a>
          </div>
      </div>
      <div id="content" class="content">
        <h1 class="h2 no-bottom-margin">%(title)s</h1>
%(searchfor)s
        <div class="collections">
          <div class="button showall">
            <a href="http://infoscience.epfl.ch/collection/Infoscience/Research?ln=%(ln)s">
              <button class="icon"></button>
              <span class="label">%(research_label)s</span>
            </a>
          </div>
          <div class="clear"></div>
          <div class="button showall">
            <a href="http://infoscience.epfl.ch/collection/Infoscience/Resource?ln=%(ln)s">
              <button class="icon"></button>
              <span class="label">%(resource_label)s</span>
            </a>
          </div>
          <div class="clear"></div>
        </div>
%(news_feed)s
        <div class="button showall">
          <a href="http://actu.epfl.ch/search/infoscience/">
            <button class="icon"></button>
            <span class="label">%(more_news_label)s</span>
          </a>
        </div>
        <a href="http://actu.epfl.ch/search/infoscience/">
      </div>
%(right_col)s
      """
        
        return body % {'title': _("Search publications"),
                       'searchfor': searchfor,
                       'ln': ln,
                       'research_label': _("Access to the %s scientific publications") % self.tmpl_nice_number_via_locale(research.nbrecs, ln),
                       'resource_label': _("Access to the %s documentary resources") % self.tmpl_nice_number_via_locale(resource.nbrecs, ln),
                       'news_feed': news_feed,
                       'more_news_label': _('More news'),
                       'right_col': self.tmpl_default_right_col(ln),
                       'feed': self.build_rss_url({'c': 'Infoscience', 'ln': ln}),
                       'feed_label': 'RSS',
                       }

    def tmpl_default_right_col(self, ln):
        """EPFL => right column """
        _ = gettext_set_language(ln)
        out = """
      <div class="right-col">
        <div class="box box-flat-panel home-navpanel local-color">
          <h3>%(title)s</h3>
          <ul>
            <li><a href="%(guidelines_url)s">%(guidelines_label)s</a></li>
            <li><a href="%(fns1_url)s">%(fns1_label)s</a></li>
            <li><a href="%(fns2_url)s">%(fns2_label)s</a></li>
            <li><a href="%(erc_url)s">%(erc_label)s</a></li>

          </ul>
        </div>
      </div>
      <div class="clear"></div>"""
        return out % { 
    'title': _("Infoscience, EPFL's scientific publications"),
                       
    'guidelines_url': ln == 'en' and 'http://polylex.epfl.ch/files/content/sites/polylex/files/recueil_pdf/ENG/3.3.2_principe_integrite_recherche_an.pdf' or 
                                     'http://polylex.epfl.ch/files/content/sites/polylex/files/recueil_pdf/3.3.2_principe_integrite_recherche_fr.pdf',
    'guidelines_label': _("EPFL Directive for Research Integrity"),
                       
    'fns1_url': ln == 'en' and 'http://www.snf.ch/SiteCollectionDocuments/allg_reglement_valorisierung_e.pdf' or 
                               'http://www.snf.ch/SiteCollectionDocuments/dos_OA_Weisung_f.pdf',
    'fns1_label': _("SNSF regulations on information, valorisation and rights to research results"),
                       
                       
    'fns2_url': ln == 'en' and 'http://www.snf.ch/SiteCollectionDocuments/Dossiers/dos_OA_regelung_auf_einen_blick_e.pdf' or 
                               'http://www.snf.ch/SiteCollectionDocuments/Dossiers/dos_OA_regelung_auf_einen_blick_f.pdf',
    'fns2_label': _("Overview of SNSF Guidelines on Open Access"),             


    'erc_url': 'http://erc.europa.eu/sites/default/files/press_release/files/open_access_policy_researchers_funded_ERC.pdf',
    'erc_label': _("Open Access Guidelines for researchers funded by the ERC"),             

}
      
              
        
    
    def tmpl_portalbox(self, title, body):
        """
        EPFL
        Creates portalboxes based on the parameters
        Parameters:
          - 'title' *string* - The title of the box
          - 'body' *string* - The HTML code for the body of the box
        """
        out = """<div class="box">
                    <h3>%(title)s</h3>
                    <p>%(body)s</p>
                 </div>""" % {'title' : title, 'body' : body}

        return out

    
    def tmpl_advanced_search_box(self, ln, ext=None):
        """ EPFL """
        _ = gettext_set_language(ln)
        
        if not ext:
            ext = []
        # ext: ['collection:ARTICLE', 'review:REVIEWED']
        out = """
            <h4>%(filter_doctype_label)s</h4>
            <ul>
              <li><h5>%(category_publications)s</h5>
                <ul>
                  <li><input type="checkbox" name="ext" value="collection:ARTICLE" id="limit-articles" %(c_article)s /><label for="limit-articles">%(ARTICLE)s</label></li>
                  <li><input type="checkbox" name="ext" value="collection:REVIEW" id="limit-reviews" %(c_review)s /><label for="limit-reviews">%(REVIEW)s</label></li>
                  <li><input type="checkbox" name="ext" value="collection:CONF" id="limit-conferences" %(c_conf)s /><label for="limit-conferences">%(CONF)s</label></li>
                </ul>
              </li>
              <li><h5>%(category_monographs)s</h5>
                <ul>
                  <li><input type="checkbox" name="ext" value="collection:BOOK" id="limit-books" %(c_book)s /><label for="limit-books">%(BOOK)s</label></li>
                  <li><input type="checkbox" name="ext" value="collection:THESIS" id="limit-theses" %(c_thesis)s /><label for="limit-theses">%(THESIS)s</label></li>
                  <li><input type="checkbox" name="ext" value="collection:CHAPTER" id="limit-chapters" %(c_chapter)s /><label for="limit-chapters">%(CHAPTER)s</label></li>
                  <li><input type="checkbox" name="ext" value="collection:PROC" id="limit-proceedings" %(c_proc)s /><label for="limit-proceedings">%(PROC)s</label></li>
                </ul>
              </li>
              <li><h5>%(category_presentations)s</h5>
                <ul>
                  <li><input type="checkbox" name="ext" value="collection:POSTER" id="limit-posters" %(c_poster)s /><label for="limit-posters">%(POSTER)s</label></li>
                  <li><input type="checkbox" name="ext" value="collection:TALK" id="limit-talks" %(c_talk)s /><label for="limit-talks">%(TALK)s</label></li>
                </ul>
              </li>
              
              <li><h5>%(category_patent)s</h5>
                <ul>
                  <li><input type="checkbox" name="ext" value="collection:STANDARD" id="limit-standards" %(c_standard)s /><label for="limit-standards">%(STANDARD)s</label></li>
                  <li><input type="checkbox" name="ext" value="collection:PATENT" id="limit-patents" %(c_patent)s /><label for="limit-patents">%(PATENT)s</label></li>
                </ul>
              </li>
              <li><h5>%(category_reports)s</h5>
                <ul>
                  <li><input type="checkbox" name="ext" value="collection:REPORT" id="limit-reports" %(c_report)s /><label for="limit-reports">%(REPORT)s</label></li>
                  <li><input type="checkbox" name="ext" value="collection:WORKING" id="limit-workingpapers" %(c_working)s /><label for="limit-workingpapers">%(WORKING)s</label></li>
                </ul>
              </li>
              <li><h5>%(category_teaching)s</h5>
                <ul>
                  <li><input type="checkbox" name="ext" value="collection:POLY" id="limit-teachingdocuments" %(c_poly)s /><label for="limit-teachingdocuments">%(POLY)s</label></li>
                  <li><input type="checkbox" name="ext" value="collection:STUDENT" id="limit-studentprojects" %(c_student)s /><label for="limit-studentprojects">%(STUDENT)s</label></li>
                </ul>
              </li>
            </ul>
            <div class="clear"></div>
            
            <ul>
              <li>
                <h4>%(filter_status_label)s</h4>
                <ul style="margin-top: 4px;">
                  <li><input type="checkbox" name="ext" value="review:REVIEWED" id="filter-review" %(c_reviewed)s /><label for="filter-review">%(REVIEWED)s</label></li>
                  <li><input type="checkbox" name="ext" value="status:PUBLISHED" id="filter-published" %(c_published)s /><label for="filter-published">%(PUBLISHED)s</label></li>
                  <li><input type="checkbox" name="ext" value="status:ACCEPTED" id="filter-accepted" %(c_accepted)s /><label for="filter-accepted">%(ACCEPTED)s</label></li>
                  <li><input type="checkbox" name="ext" value="status:SUBMITTED" id="filter-submitted" %(c_submitted)s /><label for="filter-submitted">%(SUBMITTED)s</label></li>
                </ul>
              </li>
              <li>
                <h4>%(filter_affiliation_label)s</h4>
                <ul style="margin-top: 4px;">
                  <li><input type="checkbox" name="ext" value="affiliation:EPFL" id="filter-epfl" %(c_epfl)s /><label for="filter-epfl">%(EPFL)s</label></li>
                </ul>
              </li>
            </ul>
            <div class="clear"></div>
            <ul style="margin-top: 4px;">
              <li>
                <h4>%(filter_fulltext_label)s</h4>
                <ul>
                  <li><input type="checkbox" name="ext" value="fulltext:PUBLIC" id="filter-public" %(c_public)s /><label for="filter-public">%(PUBLIC)s</label></li>
                  <li><input type="checkbox" name="ext" value="fulltext:RESTRICTED" id="filter-restricted" %(c_restricted)s /><label for="filter-restricted">%(RESTRICTED)s</label></li>
                </ul>
              </li>
            </ul>
            <div class="clear"></div>
            """
        
        return out % {'filter_doctype_label': _("Filter by document type"),
                      'category_publications': _("Publications"),
                      'ARTICLE': _("Journal Articles"), 'c_article': 'collection:ARTICLE' in ext and 'checked="checked"',
                      'REVIEW': _("Reviews"), 'c_review': 'collection:REVIEW' in ext and 'checked="checked"',
                      'CONF': _("Conference Papers"), 'c_conf': 'collection:CONF' in ext and 'checked="checked"',
                      
                      'category_monographs': _("Monographs"),
                      'BOOK': _("Books"), 'c_book': 'collection:BOOK' in ext and 'checked="checked"',
                      'THESIS': _("Theses"), 'c_thesis': 'collection:THESIS' in ext and 'checked="checked"',
                      'CHAPTER': _("Book Chapters"), 'c_chapter': 'collection:CHAPTER' in ext and 'checked="checked"',
                      'PROC': _("Conference Proceedings"), 'c_proc': 'collection:PROC' in ext and 'checked="checked"',
                      
                      'category_presentations': _("Presentations &amp; Talks"),
                      'POSTER': _("Posters"), 'c_poster': 'collection:POSTER' in ext and 'checked="checked"',
                      'TALK': _("Presentations &amp; Talks"), 'c_talk': 'collection:TALK' in ext and 'checked="checked"',
                      
                      'category_patent': _("Standards &amp; Patents"),
                      'STANDARD': _("Standards"), 'c_standard': 'collection:STANDARD' in ext and 'checked="checked"',
                      'PATENT': _("Patents"), 'c_patent': 'collection:PATENT' in ext and 'checked="checked"',                      
                      
                      'category_reports': _("Reports"),
                      'REPORT': _("Technical Reports"), 'c_report': 'collection:REPORT' in ext and 'checked="checked"',
                      'WORKING': _("Working Papers"), 'c_working': 'collection:WORKING' in ext and 'checked="checked"',
                      
                      'category_teaching': _("Lectures &amp; teaching material"),
                      'POLY': _("Teaching Documents"), 'c_poly': 'collection:POLY' in ext and 'checked="checked"',
                      'STUDENT': _("Student Projects"), 'c_student': 'collection:STUDENT' in ext and 'checked="checked"',
                        
                      'filter_status_label': _("Filter by publication status"),
                      'REVIEWED': _("Peer-reviewed publications"), 'c_reviewed': 'review:REVIEWED' in ext and 'checked="checked"',
                      'PUBLISHED': _("Published"), 'c_published': 'status:PUBLISHED' in ext and 'checked="checked"',
                      'ACCEPTED': _("Accepted"), 'c_accepted': 'status:ACCEPTED' in ext and 'checked="checked"',
                      'SUBMITTED': _("Submitted"), 'c_submitted': 'status:SUBMITTED' in ext and 'checked="checked"',
                      
                      'filter_affiliation_label': _("Filter by origin"),
                      'EPFL': _("Work produced at EPFL"), 'c_epfl': 'affiliation:EPFL' in ext and 'checked="checked"',
                      
                      'filter_fulltext_label': _("Filter by fulltext availability"),
                      'PUBLIC': _("Publicly available"), 'c_public': 'fulltext:PUBLIC' in ext and 'checked="checked"',
                      'RESTRICTED': _("Restricted access"), 'c_restricted': 'fulltext:RESTRICTED' in ext and 'checked="checked"',
                      
        
        
        
        }
        
    
    def tmpl_search_help(self, ln):
        """ EPFL : print search tips """
        _ = gettext_set_language(ln)
        help_section = """
                <h4>%(b_label)s</h4>
                <ul>
                  <li>%(and)s</li>
                  <li>%(not)s</li>
                  <li>%(or)s</li>
                </ul>
                <h4>%(p_label)s</h4>
                <p>%(paren)s</p>
                <a href="http://help-infoscience.epfl.ch/%(page)s">%(link)s</a>""" % {
                'b_label': _("Boolean operators"),
                'and': _("AND: vetterli AND wavelet <emph>(you can also use <strong>+</strong> char instead of AND)</emph>"),
                'not': _("NOT: vetterli NOT wavelet <emph>(you can also use <strong>-</strong> char instead of NOT)</emph>"),
                'or': _("OR: vetterli OR wavelet  <emph>(you can also use <strong>|</strong> char instead of OR)</emph>"),
                'p_label': _("Parentheses"),
                'paren': _("You can also use parentheses in your queries to group boolean expressions together. Nested parentheses are also supported."),
                'link': _("Full documentation about searching"),
                'page': ln == 'en' and 'search' or 'rechercher',
                }
        
        return help_section

      
    def tmpl_searchfor_simple(self, ln, collection_id, collection_name, record_count, middle_option):
        """
        EPFL
        Produces simple *Search for* box for the current collection.
        Parameters:
          - 'ln' *string* - *str* The language to display
          - 'collection_id' - *str* The collection id
          - 'collection_name' - *str* The collection name in current language
          - 'record_count' - *str* Number of records in this collection
          - 'middle_option' *string* - HTML code for the options (any field, specific fields ...)
        """
        # load the right message language
        _ = gettext_set_language(ln)
        argd = drop_default_urlargd({'ln': ln, 'cc': collection_id, 'sc': CFG_WEBSEARCH_SPLIT_BY_COLLECTION},
                                    self.search_results_default_urlargd)
        
        hidden_values = ''
        for field, value in argd.items():
            hidden_values += self.tmpl_input_hidden(field, value)
        asearchurl = self.build_search_interface_url(c=collection_id,
                                                     aas=max(CFG_WEBSEARCH_ENABLED_SEARCH_INTERFACES),
                                                     ln=ln)

        out = """
          <form id="infoscience-searchform" class="search-form" name="search" action="/search" method="get">
            %(hidden_values)s
            <input type="text" class="search" name="p" value="" id="infoscience-searchfield" /><div class="search-filter">
              %(search_within)s
            </div><button type="submit" class="search-button" title="%(label)s">%(label)s</button>
            <div class="clear"></div>
            <div class="helper">
              <a href="http://help-infoscience.epfl.ch/%(search_url)s" class="label" id="search-help">%(help_label)s</a>
              <div class="tooltip bottom">
%(help_section)s
              </div>
            </div>
            <div class="toggler">
              <a href="%(asearch_url)s" class="label">%(advanced_label)s</a>
            </div>
            <div class="toggled" id="advanced-search" style="display: none">
%(advanced_box)s
            </div>
          </form>"""

        return out % {'siteurl' : CFG_SITE_URL,
                      'hidden_values': hidden_values,
                      'search_within': middle_option,
                      'asearch_url': asearchurl,
                      'search_url': ln=='en' and 'search' or 'rechercher',
                      'label': _("Search"),
                      'help_label': _("Search Tips"),
                      'advanced_label': _("Advanced Search"),
                      'advanced_box': self.tmpl_advanced_search_box(ln),
                      'help_section': self.tmpl_search_help(ln),
                     }


    def tmpl_searchfor_advanced(self,
                                ln,                  # current language
                                collection_id,
                                collection_name,
                                record_count,
                                middle_option_1, middle_option_2, middle_option_3,
                                searchoptions,
                                sortoptions,
                                rankoptions,
                                displayoptions,
                                formatoptions
                                ):
        """
          Produces advanced *Search for* box for the current collection.
          Parameters:
            - 'ln' *string* - The language to display
            - 'middle_option_1' *string* - HTML code for the first row of options (any field, specific fields ...)
            - 'middle_option_2' *string* - HTML code for the second row of options (any field, specific fields ...)
            - 'middle_option_3' *string* - HTML code for the third row of options (any field, specific fields ...)
            - 'searchoptions' *string* - HTML code for the search options
            - 'sortoptions' *string* - HTML code for the sort options
            - 'rankoptions' *string* - HTML code for the rank options
            - 'displayoptions' *string* - HTML code for the display options
            - 'formatoptions' *string* - HTML code for the format options
        """
        # load the right message language
        _ = gettext_set_language(ln)

        out = '''
        <!--create_searchfor_advanced()-->
        '''
        argd = drop_default_urlargd({'ln': ln, 'aas': 1, 'cc': collection_id, 'sc': CFG_WEBSEARCH_SPLIT_BY_COLLECTION},
                                    self.search_results_default_urlargd)

        # Only add non-default hidden values
        for field, value in argd.items():
            out += self.tmpl_input_hidden(field, value)


        header = _("Search %s records for") % \
                 self.tmpl_nbrecs_info(record_count, "", "")
        header += ':'
        ssearchurl = self.build_search_interface_url(c=collection_id, aas=min(CFG_WEBSEARCH_ENABLED_SEARCH_INTERFACES), ln=ln)

        out += '''
        <table class="searchbox advancedsearch">
         <thead>
          <tr>
           <th class="searchboxheader" colspan="3">%(header)s</th>
          </tr>
         </thead>
         <tbody>
          <tr valign="bottom">
            <td class="searchboxbody" style="white-space: nowrap;">
                %(matchbox_m1)s<input type="text" name="p1" size="%(sizepattern)d" value="" class="advancedsearchfield"/>
            </td>
            <td class="searchboxbody" style="white-space: nowrap;">%(middle_option_1)s</td>
            <td class="searchboxbody">%(andornot_op1)s</td>
          </tr>
          <tr valign="bottom">
            <td class="searchboxbody" style="white-space: nowrap;">
                %(matchbox_m2)s<input type="text" name="p2" size="%(sizepattern)d" value="" class="advancedsearchfield"/>
            </td>
            <td class="searchboxbody">%(middle_option_2)s</td>
            <td class="searchboxbody">%(andornot_op2)s</td>
          </tr>
          <tr valign="bottom">
            <td class="searchboxbody" style="white-space: nowrap;">
                %(matchbox_m3)s<input type="text" name="p3" size="%(sizepattern)d" value="" class="advancedsearchfield"/>
            </td>
            <td class="searchboxbody">%(middle_option_3)s</td>
            <td class="searchboxbody" style="white-space: nowrap;">
              <input class="formbutton" type="submit" name="action_search" value="%(msg_search)s" />
              <input class="formbutton" type="submit" name="action_browse" value="%(msg_browse)s" /></td>
          </tr>
          <tr valign="bottom">
            <td colspan="3" class="searchboxbody" align="right">
              <small>
                <a href="%(siteurl)s/help/search-tips%(langlink)s">%(msg_search_tips)s</a> ::
                %(ssearch)s
              </small>
            </td>
          </tr>
         </tbody>
        </table>
        <!-- @todo - more imports -->
        ''' % {'ln' : ln,
               'sizepattern' : CFG_WEBSEARCH_ADVANCEDSEARCH_PATTERN_BOX_WIDTH,
               'langlink': ln != CFG_SITE_LANG and '?ln=' + ln or '',
               'siteurl' : CFG_SITE_URL,
               'ssearch' : create_html_link(ssearchurl, {}, _("Simple Search")),
               'header' : header,

               'matchbox_m1' : self.tmpl_matchtype_box('m1', ln=ln),
               'middle_option_1' : middle_option_1,
               'andornot_op1' : self.tmpl_andornot_box('op1', ln=ln),

               'matchbox_m2' : self.tmpl_matchtype_box('m2', ln=ln),
               'middle_option_2' : middle_option_2,
               'andornot_op2' : self.tmpl_andornot_box('op2', ln=ln),

               'matchbox_m3' : self.tmpl_matchtype_box('m3', ln=ln),
               'middle_option_3' : middle_option_3,

               'msg_search' : _("Search"),
               'msg_browse' : _("Browse"),
               'msg_search_tips' : _("Search Tips")}

        if (searchoptions):
            out += """<table class="searchbox">
                      <thead>
                       <tr>
                         <th class="searchboxheader">
                           %(searchheader)s
                         </th>
                       </tr>
                      </thead>
                      <tbody>
                       <tr valign="bottom">
                        <td class="searchboxbody">%(searchoptions)s</td>
                       </tr>
                      </tbody>
                     </table>""" % {
                       'searchheader' : _("Search options:"),
                       'searchoptions' : searchoptions
                     }

        out += """<table class="searchbox">
                   <thead>
                    <tr>
                      <th class="searchboxheader">
                        %(added)s
                      </th>
                      <th class="searchboxheader">
                        %(until)s
                      </th>
                    </tr>
                   </thead>
                   <tbody>
                    <tr valign="bottom">
                      <td class="searchboxbody">%(added_or_modified)s %(date_added)s</td>
                      <td class="searchboxbody">%(date_until)s</td>
                    </tr>
                   </tbody>
                  </table>
                  <table class="searchbox">
                   <thead>
                    <tr>
                      <th class="searchboxheader">
                        %(msg_sort)s
                      </th>
                      <th class="searchboxheader">
                        %(msg_display)s
                      </th>
                      <th class="searchboxheader">
                        %(msg_format)s
                      </th>
                    </tr>
                   </thead>
                   <tbody>
                    <tr valign="bottom">
                      <td class="searchboxbody">%(sortoptions)s %(rankoptions)s</td>
                      <td class="searchboxbody">%(displayoptions)s</td>
                      <td class="searchboxbody">%(formatoptions)s</td>
                    </tr>
                   </tbody>
                  </table>
                  <!--/create_searchfor_advanced()-->
              """ % {

                    'added' : _("Added/modified since:"),
                    'until' : _("until:"),
                    'added_or_modified': self.tmpl_inputdatetype(ln=ln),
                    'date_added' : self.tmpl_inputdate("d1", ln=ln),
                    'date_until' : self.tmpl_inputdate("d2", ln=ln),

                    'msg_sort' : _("Sort by:"),
                    'msg_display' : _("Display results:"),
                    'msg_format' : _("Output format:"),
                    'sortoptions' : sortoptions,
                    'rankoptions' : rankoptions,
                    'displayoptions' : displayoptions,
                    'formatoptions' : formatoptions
                  }
        return out

    def tmpl_narrowsearch(self, aas, ln, type, father,
                          has_grandchildren, sons, display_grandsons,
                          grandsons):

        """
        EPFL
        Creates list of collection descendants of type *type* under title *title*.
        If aas==1, then links to Advanced Search interfaces; otherwise Simple Search.
        Suitable for 'Narrow search' and 'Focus on' boxes.

        Parameters:
          - 'aas' *bool* - Should we display an advanced search box?
          - 'ln' *string* - The language to display
          - 'type' *string* - The type of the produced box (virtual collections or normal collections)
          - 'father' *collection* - The current collection
          - 'has_grandchildren' *bool* - If the current collection has grand children
          - 'sons' *list* - The list of the sub-collections (first level)
          - 'display_grandsons' *bool* - If the grand children collections should be displayed (2 level deep display)
          - 'grandsons' *list* - The list of sub-collections (second level)
        """
        _ = gettext_set_language(ln)        
        out = """
            <li class="open">
              %(label)s
              <ul>
%(subcollections)s
              </ul>
            </li>"""
        
        if type == 'r':
            label = _("Search specifically in")
        elif type == 'v':
            label = _("Focus on")

        son_accro_tmpl = """
                <li>
                  <a href="%(url)s"><acronym>%(acronym)s</acronym> %(name)s %(nb)s</a>
                  %(grandchildren)s
                </li>"""
        grandson_accro_tmpl = """
                    <li>
                      <a href="%(url)s"><acronym>%(acronym)s</acronym> %(name)s %(nb)s</a>
                    </li>"""
        son_tmpl = """
                <li>
                  <a href="%(url)s">%(name)s %(nb)s</a>
                  %(grandchildren)s
                </li>"""
        grandson_tmpl = """
                    <li>
                      <a href="%(url)s">%(name)s %(nb)s</a>
                    </li>"""
        subcollections = []
        for son_index, son in enumerate(sons):
            try:
                (acronym, name) = son.get_name(ln).split(' - ')
                tmpl = son_accro_tmpl
            except ValueError:
                acronym = ''
                name = son.get_name(ln)
                tmpl = son_tmpl
                
            grandchildren = ''
            if has_grandchildren:
                grandchildren = """
                  <ul>
%s
                  </ul>"""
                subsubcollections = []
                for grandson in grandsons[son_index]:
                    try:
                        (subacronym, subname) = grandson.get_name(ln).split(' - ')
                        grand_tmpl = grandson_accro_tmpl
                    except ValueError:
                        (subacronym, subname) = ('', grandson.get_name(ln))
                        grand_tmpl = grandson_tmpl
                    subsubcollections.append(grand_tmpl % {'url': self.build_search_interface_url(c=grandson.name, ln=ln, aas=aas),
                                                           'acronym': subacronym,
                                                           'name': subname,
                                                           'nb': self.tmpl_nbrecs_info(grandson.nbrecs, ln=ln) })
                grandchildren %=''.join(subsubcollections)
            
            subcollections.append(tmpl % {'url': self.build_search_interface_url(c=son.name, ln=ln, aas=aas),
                                          'acronym': acronym,
                                          'name': name,
                                          'nb': self.tmpl_nbrecs_info(son.nbrecs, ln=ln),
                                          'grandchildren': grandchildren })

        return out % {'label': label, 
                      'subcollections': '\n'.join(subcollections)}
    
    
    def tmpl_instant_browse(self, aas, ln, recids, more_link = None):
        """
        EPFL
        Formats a list of records (given in the recids list) from the database.
        Parameters:
          - 'aas' *int* - Advanced Search interface or not (0 or 1)
          - 'ln' *string* - The language to display
          - 'recids' *list* - the list of records from the database
          - 'more_link' *string* - the "More..." link for the record. If not given, will not be displayed
        """
        # load the right message language
        _ = gettext_set_language(ln)
        body = """
            <ul class="infoscience_export latest_additions">"""
        for recid in recids:
            body += """
              <li class="infoscience_record infoscience_record_bulleted">
                <div class="infoscience_bullet date">%(date)s</div>
                <div class="infoscience_data">
                  <abbr class="unapi-id" title="%(recid)s"></abbr>
                  %(body)s
                </div>
              </li>""" % {
                        'recid': recid['id'],
                        'date': recid['date'],
                        'body': recid['body']
                      }
        body += """
            </ul>"""
        if more_link:
            body += '<div align="right"><small>' + \
                    create_html_link(more_link, {}, '[&gt;&gt; %s]' % _("more")) + \
                    '</small></div>'
        return body

    
    def tmpl_searchwithin_select(self, ln, fieldname, selected, values):
        """
        EPFL
        Produces 'search within' selection box for the current collection.
        Parameters:
          - 'ln' *string* - The language to display
          - 'fieldname' *string* - the name of the select box produced
          - 'selected' *string* - which of the values is selected
          - 'values' *list* - the list of values in the select
        """
        _ = gettext_set_language(ln)
        out = """
            <a href="#" id="selected-field">%s</a>
            <ul class="menu hidden">
%s
            </ul>
        """
        tmpl = """
              <li>
                <input type="radio" name="%(fieldname)s" id="field-%(value)s" value="%(value)s" %(checked)s />
                <label for="field-%(value)s" %(checked_class)s>%(label)s</label>
              </li>"""

        values = [{'value': '', 'text': _("Any field")},
                  {'value': 'title', 'text': _("Title")},
                  {'value': 'author', 'text': _("Author")},
                  {'value': 'keyword', 'text': _("Keyword")},
                  {'value': 'year', 'text': _("Year")},
                  {'value': 'source', 'text': _("Source")},
                  {'value': 'reportnumber', 'text': _("Report number")},
                  {'value': 'doi', 'text': _("DOI")},]
        lines = []
        s_label = _("Any field")
        for pair in values:
            lines.append(tmpl % {'fieldname': fieldname, 'value': pair['value'],
                                'label': pair['text'],
                                'checked': pair['value'] == selected and 'checked="checked"' or '',
                                'checked_class': pair['value'] == selected and 'class="current"' or ''})
            if selected == pair['value']:
                s_label = pair['text'] 
            
        return out % (s_label, ''.join(lines))


    def tmpl_record_links(self, recid, ln, sf='', so='d', sp='', rm=''):
        """
        EPFL
        Displays the *More info* and *Find similar* links for a record
        Parameters:
          - 'ln' *string* - The language to display
          - 'recid' *string* - the id of the displayed record
        """
        return self.tmpl_print_record_brief_links(ln=ln, recID=recid, sf=sf, so=so, sp=sp, rm=rm, user_info=None)

    def tmpl_search_in_bibwords(self, p, f, ln, nearest_box):
        """
          Displays the *Words like current ones* links for a search

        Parameters:

          - 'p' *string* - Current search words

          - 'f' *string* - the fields in which the search was done

          - 'nearest_box' *string* - the HTML code for the "nearest_terms" box - most probably from a create_nearest_terms_box call
        """

        # load the right message language
        _ = gettext_set_language(ln)
        out = '<p>'
        if f:
            out += _("Words nearest to %(x_word)s inside %(x_field)s in any collection are:") % {'x_word': '<em>' + cgi.escape(p) + '</em>',
                                                                                                 'x_field': '<em>' + cgi.escape(f) + '</em>'}
        else:
            out += _("Words nearest to %(x_word)s in any collection are:") % {'x_word': '<em>' + cgi.escape(p) + '</em>'}
        out += '<br />' + nearest_box + '</p>'
        return out

    def tmpl_nearest_term_box(self, p, ln, f, terminfo, intro):
        """
        EPFL
          Displays the *Nearest search terms* box
        Parameters:
          - 'p' *string* - Current search words
          - 'f' *string* - a collection description (if the search has been completed in a collection)
          - 'ln' *string* - The language to display
          - 'terminfo': tuple (term, hits, argd) for each near term
          - 'intro' *string* - the intro HTML to prefix the box with
        """
        _ = gettext_set_language(ln)
        out = """
%s
          <ul class="nearest-box">
%s
          </ul>
        """
        tmpl = """
            <li>%(term)s (%(hits)s)</li>"""
            
        definitions = []
        for term, hits, argd in terminfo:
            if hits:
                hitsinfo = _("%s results") % str(hits)
            else:
                hitsinfo = _("%s results") % str(0)
            term = cgi.escape(term)
            if term == p: # print search word for orientation:
                if hits > 0:
                    term = create_html_link(self.build_search_url(argd), {}, term)
            else:
                term = create_html_link(self.build_search_url(argd), {}, term)
            definitions.append(tmpl % {'hits': hitsinfo, 'term': term})
    
        return out % (intro, ''.join(definitions))

    def tmpl_browse_pattern(self, f, fn, ln, browsed_phrases_in_colls, colls, rg):
        """
          Displays the *Nearest search terms* box

        Parameters:

          - 'f' *string* - field (*not* i18nized)

          - 'fn' *string* - field name (i18nized)

          - 'ln' *string* - The language to display

          - 'browsed_phrases_in_colls' *array* - the phrases to display

          - 'colls' *array* - the list of collection parameters of the search (c's)

          - 'rg' *int* - the number of records
        """

        # load the right message language
        _ = gettext_set_language(ln)

        out = """<table class="searchresultsbox">
              <thead>
               <tr>
                <th class="searchresultsboxheader" style="text-align: right;" width="15">
                  %(hits)s
                </th>
                <th class="searchresultsboxheader" width="15">
                  &nbsp;
                </th>
                <th class="searchresultsboxheader" style="text-align: left;">
                  %(fn)s
                </th>
               </tr>
              </thead>
              <tbody>""" % {
                'hits' : _("Hits"),
                'fn' : cgi.escape(fn)
              }

        if len(browsed_phrases_in_colls) == 1:
            # one hit only found:
            phrase, nbhits = browsed_phrases_in_colls[0][0], browsed_phrases_in_colls[0][1]

            query = {'c': colls,
                     'ln': ln,
                     'p': '"%s"' % phrase.replace('"', '\\"'),
                     'f': f,
                     'rg' : rg}

            out += """<tr>
                       <td class="searchresultsboxbody" style="text-align: right;">
                        %(nbhits)s
                       </td>
                       <td class="searchresultsboxbody" width="15">
                        &nbsp;
                       </td>
                       <td class="searchresultsboxbody" style="text-align: left;">
                        %(link)s
                       </td>
                      </tr>""" % {'nbhits': nbhits,
                                  'link': create_html_link(self.build_search_url(query),
                                                           {}, cgi.escape(phrase))}

        elif len(browsed_phrases_in_colls) > 1:
            # first display what was found but the last one:
            for phrase, nbhits in browsed_phrases_in_colls[:-1]:
                query = {'c': colls,
                         'ln': ln,
                         'p': '"%s"' % phrase.replace('"', '\\"'),
                         'f': f,
                         'rg' : rg}

                out += """<tr>
                           <td class="searchresultsboxbody" style="text-align: right;">
                            %(nbhits)s
                           </td>
                           <td class="searchresultsboxbody" width="15">
                            &nbsp;
                           </td>
                           <td class="searchresultsboxbody" style="text-align: left;">
                            %(link)s
                           </td>
                          </tr>""" % {'nbhits' : nbhits,
                                      'link': create_html_link(self.build_search_url(query),
                                                               {},
                                                               cgi.escape(phrase))}

            # now display last hit as "previous term":
            phrase, nbhits = browsed_phrases_in_colls[0]
            query_previous = {'c': colls,
                     'ln': ln,
                     'p': '"%s"' % phrase.replace('"', '\\"'),
                     'f': f,
                     'rg' : rg}

            # now display last hit as "next term":
            phrase, nbhits = browsed_phrases_in_colls[-1]
            query_next = {'c': colls,
                     'ln': ln,
                     'p': '"%s"' % phrase.replace('"', '\\"'),
                     'f': f,
                     'rg' : rg}

            out += """<tr><td colspan="2" class="normal">
                            &nbsp;
                          </td>
                          <td class="normal">
                            %(link_previous)s
                            <img src="%(siteurl)s/img/sp.gif" alt="" border="0" />
                            <img src="%(siteurl)s/img/sn.gif" alt="" border="0" />
                            %(link_next)s
                          </td>
                      </tr>""" % {'link_previous': create_html_link(self.build_search_url(query_previous, action='browse'), {}, _("Previous")),
                      'link_next': create_html_link(self.build_search_url(query_next, action='browse'),
                                                           {}, _("next")),
                                  'siteurl' : CFG_SITE_URL}
        out += """</tbody>
            </table>"""
        return out

    def tmpl_search_box(self, ln, aas, cc, cc_intl, ot, sp,
                        action, fieldslist, f1, f2, f3, m1, m2, m3,
                        p1, p2, p3, op1, op2, rm, p, f, coll_selects,
                        d1y, d2y, d1m, d2m, d1d, d2d, dt, sort_fields,
                        sf, so, ranks, sc, rg, formats, of, pl, jrec, ec,
                        show_colls=True, show_title=True, ext=None):

        """
        EPFL
        Displays the *Nearest search terms* box
        Parameters:
          - 'ln' *string* - The language to display
          - 'aas' *bool* - Should we display an advanced search box? -1 -> 1, from simpler to more advanced
          - 'cc_intl' *string* - the i18nized current collection name, used for display
          - 'cc' *string* - the internal current collection name
          - 'ot', 'sp' *string* - hidden values
          - 'action' *string* - the action demanded by the user
          - 'fieldslist' *list* - the list of all fields available, for use in select within boxes in advanced search
          - 'p, f, f1, f2, f3, m1, m2, m3, p1, p2, p3, op1, op2, op3, rm' *strings* - the search parameters
          - 'coll_selects' *array* - a list of lists, each containing the collections selects to display
          - 'd1y, d2y, d1m, d2m, d1d, d2d' *int* - the search between dates
          - 'dt' *string* - the dates' types (creation dates, modification dates)
          - 'sort_fields' *array* - the select information for the sort fields
          - 'sf' *string* - the currently selected sort field
          - 'so' *string* - the currently selected sort order ("a" or "d")
          - 'ranks' *array* - ranking methods
          - 'rm' *string* - selected ranking method
          - 'sc' *string* - split by collection or not
          - 'rg' *string* - selected results/page
          - 'formats' *array* - available output formats
          - 'of' *string* - the selected output format
          - 'pl' *string* - `limit to' search pattern
          - show_colls *bool* - propose coll selection box?
          - show_title *bool* show cc_intl in page title?
        """
        # load the right message language
        _ = gettext_set_language(ln)
        out = ""
        
        if aas == -1:
            argd = drop_default_urlargd({
                'ln': ln, 'aas': aas,
                'ot': ot, 'sp': sp, 'ec': ec,
                }, self.search_results_default_urlargd)
        else:
            argd = drop_default_urlargd({
                'cc': cc, 'ln': ln, 'aas': aas,
                'ot': ot, 'sp': sp, 'ec': ec,
                }, self.search_results_default_urlargd)

        asearchurl = self.build_search_interface_url(c=cc, **argd)

        if show_title:
            out += """
        <h1 class="h2 no-bottom-margin">%(ccname)s</h1>"""
        else:
            out += """
        <h1 class="h2 no-bottom-margin">%s</h1>""" % _("Search results")

        out += """
          <form id="infoscience-searchform" class="search-form" name="search" action="/search" method="get">
            %(hidden_fields)s
            <input type="text" class="search" name="p" value="%(pattern)s" id="infoscience-searchfield" /><div class="search-filter">
%(search_within)s        
            </div><button type="submit" class="search-button" title="%(label)s">%(label)s</button>
            <div class="clear"></div>
            <div class="helper" >
              <a href="http://help-infoscience.epfl.ch/search" class="label" id="search-help">%(help_label)s</a>
              <div class="tooltip bottom">
%(help_section)s
              </div>
            </div>
            <div class="toggler %(advanced_class)s">
              <a href="%(asearch_url)s" class="label">%(advanced_label)s</a>
            </div>
            <div class="toggled" id="advanced-search" %(toggled)s>
%(advanced_box)s
            </div>
          </form>
        """             
        return out % {'ccname': cc_intl,
                      'hidden_fields': ''.join([self.tmpl_input_hidden(field, value) for (field, value) in argd.items()]),
                      'search_within': self.tmpl_searchwithin_select(ln=ln, fieldname='f', selected=f, values=[]),
                      'advanced_class': aas == 1 and 'toggled-active' or '',
                      'toggled': aas == 0 and 'style="display: none"' or '',
                      'pattern': aas==0 and p or p1,
                      'asearch_url': asearchurl,
                      'label': _("Search"),
                      'help_label': _("Search Tips"),
                      'advanced_label': _("Advanced Search"),
                      'advanced_box': self.tmpl_advanced_search_box(ln, ext),
                      'help_section': self.tmpl_search_help(ln),
                      }
        
        if show_colls and aas > -1:
            # display collections only if there is more than one
            selects = ''
            for sel in coll_selects:
                selects += self.tmpl_select(fieldname='c', values=sel)

            out += """
                <table class="searchbox">
                 <thead>
                  <tr>
                   <th colspan="3" class="searchboxheader">
                    %(leading)s %(msg_coll)s:
                   </th>
                  </tr>
                 </thead>
                 <tbody>
                  <tr valign="bottom">
                   <td valign="top" class="searchboxbody">
                     %(colls)s
                   </td>
                  </tr>
                 </tbody>
                </table>
                 """ % {
                   'leading' : leadingtext,
                   'msg_coll' : _("collections"),
                   'colls' : selects,
                 }

        ## thirdly, print search limits, if applicable:
        if action != _("Browse") and pl:
            out += """<table class="searchbox">
                       <thead>
                        <tr>
                          <th class="searchboxheader">
                            %(limitto)s
                          </th>
                        </tr>
                       </thead>
                       <tbody>
                        <tr valign="bottom">
                          <td class="searchboxbody">
                           <input type="text" name="pl" size="%(sizepattern)d" value="%(pl)s" />
                          </td>
                        </tr>
                       </tbody>
                      </table>""" % {
                        'limitto' : _("Limit to:"),
                        'sizepattern' : CFG_WEBSEARCH_ADVANCEDSEARCH_PATTERN_BOX_WIDTH,
                        'pl' : cgi.escape(pl, 1),
                      }

        ## fourthly, print from/until date boxen, if applicable:
        if action == _("Browse") or (d1y==0 and d1m==0 and d1d==0 and d2y==0 and d2m==0 and d2d==0):
            pass # do not need it
        else:
            cell_6_a = self.tmpl_inputdatetype(dt, ln) + self.tmpl_inputdate("d1", ln, d1y, d1m, d1d)
            cell_6_b = self.tmpl_inputdate("d2", ln, d2y, d2m, d2d)
            out += """<table class="searchbox">
                       <thead>
                        <tr>
                          <th class="searchboxheader">
                            %(added)s
                          </th>
                          <th class="searchboxheader">
                            %(until)s
                          </th>
                        </tr>
                       </thead>
                       <tbody>
                        <tr valign="bottom">
                          <td class="searchboxbody">%(added_or_modified)s %(date1)s</td>
                          <td class="searchboxbody">%(date2)s</td>
                        </tr>
                       </tbody>
                      </table>""" % {
                        'added' : _("Added/modified since:"),
                        'until' : _("until:"),
                        'added_or_modified': self.tmpl_inputdatetype(dt, ln),
                        'date1' : self.tmpl_inputdate("d1", ln, d1y, d1m, d1d),
                        'date2' : self.tmpl_inputdate("d2", ln, d2y, d2m, d2d),
                      }

        ## fifthly, print Display results box, including sort/rank, formats, etc:
        if action != _("Browse") and aas > -1:

            rgs = []
            for i in [10, 25, 50, 100, 250, 500]:
                if i <= CFG_WEBSEARCH_MAX_RECORDS_IN_GROUPS:
                    rgs.append({ 'value' : i, 'text' : "%d %s" % (i, _("results"))})
            # enrich sort fields list if we are sorting by some MARC tag:
            sort_fields = self._add_mark_to_field(value=sf, fields=sort_fields, ln=ln)
            # create sort by HTML box:
            out += """<table class="searchbox">
                 <thead>
                  <tr>
                   <th class="searchboxheader">
                    %(sort_by)s
                   </th>
                   <th class="searchboxheader">
                    %(display_res)s
                   </th>
                   <th class="searchboxheader">
                    %(out_format)s
                   </th>
                  </tr>
                 </thead>
                 <tbody>
                  <tr valign="bottom">
                   <td valign="top" class="searchboxbody">
                     %(select_sf)s %(select_so)s %(select_rm)s
                   </td>
                   <td valign="top" class="searchboxbody">
                     %(select_rg)s %(select_sc)s
                   </td>
                   <td valign="top" class="searchboxbody">%(select_of)s</td>
                  </tr>
                 </tbody>
                </table>""" % {
                  'sort_by' : _("Sort by:"),
                  'display_res' : _("Display results:"),
                  'out_format' : _("Output format:"),
                  'select_sf' : self.tmpl_select(fieldname = 'sf', values = sort_fields, selected = sf, css_class = 'address'),
                  'select_so' : self.tmpl_select(fieldname = 'so', values = [{
                                    'value' : 'a',
                                    'text' : _("asc.")
                                  }, {
                                    'value' : 'd',
                                    'text' : _("desc.")
                                  }], selected = so, css_class = 'address'),
                  'select_rm' : self.tmpl_select(fieldname = 'rm', values = ranks, selected = rm, css_class = 'address'),
                  'select_rg' : self.tmpl_select(fieldname = 'rg', values = rgs, selected = rg, css_class = 'address'),
                  'select_sc' : self.tmpl_select(fieldname = 'sc', values = [{
                                    'value' : 0,
                                    'text' : _("single list")
                                  }, {
                                    'value' : 1,
                                    'text' : _("split by collection")
                                  }], selected = sc, css_class = 'address'),
                  'select_of' : self.tmpl_select(
                                  fieldname = 'of',
                                  selected = of,
                                  values = self._add_mark_to_field(value=of, fields=formats, chars=3, ln=ln),
                                  css_class = 'address'),
                }

        ## last but not least, print end of search box:
        out += """</form>"""
        return out
    

    def tmpl_search_pagestart(self, user_info, rss_url='', ln=CFG_SITE_LANG) :
        "EPFL page start for search page. Will display after the page header"
        _ = gettext_set_language(ln)
        rss_button = ''
        basket_button = ''
        
        if rss_url:
            rss_button = """
          <div class="button feed">
            <a href="%s">
              <button class="icon"></button>
              <span class="label">RSS</span>
            </a>
          </div>""" % rss_url
        
        basket_modal = ''
        if user_info and not int(user_info.get('guest', '1')):
            uid = user_info.get('uid', -1)
            import invenio.webbasket_dblayer as db
            personal_basket_list = db.get_all_personal_basket_ids_and_names_by_topic_for_add_to_list(uid)
            group_basket_list = db.get_all_group_basket_ids_and_names_by_group_for_add_to_list(uid)
            from invenio.webbasket_templates_epfl import create_add_box_select_options
            options = create_add_box_select_options('', '', personal_basket_list, group_basket_list, ln)
            basket_modal = """
          <div class="modal" id="basket_modal">
            <h3>%(title)s</h3>
            <form name="add_to_basket" id="add-form" method="post" action="/yourbaskets/add">
              <div class="modal-content">
                <label for="basket-selection">%(choose_basket_label)s</label>
                <select name="b">
                  %(baskets_list)s
                </select><br />
                <span>%(create_label)s</span> <span id="basket-error-message" style="color: #ae0010; display: none">%(mandatory_label)s</span>
              </div>
              <div class="navigation-bar">
                <div class="group right">
                  <button type="submit" class="default" value="%(submit_label)s">%(submit_label)s</button>
                  <button type="reset" class="close" value="%(cancel_label)s">%(cancel_label)s</button>
                </div>
              </div>
            </form>
          </div>""" % {'title': _("Add record to collection"),
                       'choose_basket_label': _("Please choose a collection"),
                       'create_label': _("or %(x_url_open)screate a new one%(x_url_close)s first") % {'x_url_open': '<a href="/yourbaskets/create_basket?ln=%s">' % ln, 'x_url_close': '</a>'},
                       'baskets_list': options,
                       'mandatory_label': _("This field is required"),
                       'submit_label': _("Add record"),
                       'cancel_label': _("Cancel")}
        
            
        out = """
        <div id="tools">
%(rss)s
          <div class="button file" style="display: none">
            <div id="tooltip_trigger">
                <a href="" id="convert_records">
                  <button class="icon"></button>
                  <span class="label">%(export_label)s</span>
                </a>
            </div>

            <div class="tooltip bottom">
              <ul id="convert_formats">
                <li><a href="/curator/convert/bibtex">BibTeX</a></li>
                <li><a href="/curator/convert/dublincore">Dublin Core XML</a></li>
                <li><a href="/curator/convert/ris">RIS (RefMan, EndNote)</a></li>
                <li><a href="/curator/convert/marcxml">MARC XML</a></li>
              </ul>
            </div>                    

            <div class="clear"></div>
          </div>

          <div class="button link" style="display: none">
            <a href="#" id="export_web">
              <button class="icon"></button>
              <span class="label">%(export_web_label)s</span>
            </a>
            <div class="clear"></div>
          </div>
                    
        </div>
        <div id="content" class="content">
%(basket_modal)s""" 
        return out % {'rss': rss_button, 'basket_modal': basket_modal, 
                      'export_label': _('Export'), 
                      'export_web_label': _("Integrate these publications into my website")}

    def tmpl_search_pageend(self, ln) :
        "EPFL page end for search page. Will display just before the page footer"
        _ = gettext_set_language(ln)
        out = """
        </div>
        """
        return out

    def tmpl_print_warning(self, msg, type, prologue, epilogue):
        """
        EPFL
        Prints warning message and flushes output.
        Parameters:
          - 'msg' *string* - The message string
          - 'type' *string* - the warning type
          - 'prologue' *string* - HTML code to display before the warning
          - 'epilogue' *string* - HTML code to display after the warning
        """
        out = """
          <p class="quicknote">%s</p>"""
        if type:
            msg = '%s: %s' % (type, msg)
        return out % msg

    def tmpl_pagination(self, query_params, nb_recs, recs_per_page, jrec, ln):
        """EPFL
        """
        def get_link(page):
            if not 'rg' in query_params:
                return self.build_search_url(jrec= 1 + (page -1) * recs_per_page, rg=recs_per_page, **query_params)
            return self.build_search_url(jrec= 1 + (page -1) * recs_per_page, **query_params)
        
        _ = gettext_set_language(ln)
                
        LEADING_PAGE_RANGE_DISPLAYED = TRAILING_PAGE_RANGE_DISPLAYED = 5
        LEADING_PAGE_RANGE = TRAILING_PAGE_RANGE = 4
        NUM_PAGES_OUTSIDE_RANGE = 2
        ADJACENT_PAGES = 2
        
        in_leading_range = in_trailing_range = False
        pages_outside_leading_range = pages_outside_trailing_range = range(0)
        
        total_nb_pages = int(math.ceil(float(nb_recs) / float(recs_per_page)))
        current_page = (jrec / recs_per_page) + 1
        
        if total_nb_pages <= LEADING_PAGE_RANGE_DISPLAYED:
            in_leading_range = in_trailing_range = True
            page_numbers = [n for n in range(1, total_nb_pages + 1)]
            
        elif current_page <= LEADING_PAGE_RANGE:
            in_leading_range = True
            page_numbers = [n for n in range(1, LEADING_PAGE_RANGE_DISPLAYED + 1) if n > 0 and n <= total_nb_pages]
            pages_outside_leading_range = [n + total_nb_pages for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
            pages_outside_leading_range.reverse()
            
        elif current_page > total_nb_pages - TRAILING_PAGE_RANGE:
            in_trailing_range = True
            page_numbers = [n for n in range(total_nb_pages - TRAILING_PAGE_RANGE_DISPLAYED + 1, total_nb_pages + 1) if n > 0 and n <= total_nb_pages]
            pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
            
        else:
            page_numbers = [n for n in range(current_page - ADJACENT_PAGES, current_page + ADJACENT_PAGES + 1) if n > 0 and n <= total_nb_pages]
            pages_outside_leading_range = [n + total_nb_pages for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
            pages_outside_leading_range.reverse()
            pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
                
        page_tmpl = """
            <li><a href="%s" %s>%s</a></li>"""
        separator = """
            <li>...</li>"""
        
        out = """
        <div class="pagination">
          <ul>"""
        if current_page > 1:
            out += """
            <li><a href="%s">%s</a></li>""" % (get_link(current_page - 1), _("Previous"))
        else:
            out += """
            <li>%s</li>""" % _("Previous")
        
        if not in_leading_range:
            out += '\n'.join([page_tmpl % (get_link(nb), '', nb) 
                              for nb in pages_outside_trailing_range])
            out += separator
        
        out += '\n'.join([page_tmpl % (get_link(nb), nb==current_page and 'class="current"', nb) 
                          for nb in page_numbers])

        if not in_trailing_range:
            out += separator
            out += '\n'.join([page_tmpl % (get_link(nb), '', nb) 
                              for nb in pages_outside_leading_range])
        
        if current_page < total_nb_pages:
            out += """
            <li><a href="%s">%s</a></li>""" % (get_link(current_page + 1), _("Next"))
        else:
            out += """
            <li>%s</li>""" % _("Next")
        
        out += """
          </ul>
        </div>
        <div class="clear"></div>"""
        return out             
        

    def tmpl_print_search_info(self, ln, middle_only,
                               collection, collection_name, collection_id,
                               aas, sf, so, rm, rg, nb_found, of, ot, p, f, f1,
                               f2, f3, m1, m2, m3, op1, op2, p1, p2,
                               p3, d1y, d1m, d1d, d2y, d2m, d2d, dt,
                               all_fieldcodes, cpu_time, pl_in_url,
                               jrec, sc, sp, ext):

        """
        EPFL
        Prints stripe with the information on 'collection' and 'nb_found' results and CPU time.
           Also, prints navigation links (beg/next/prev/end) inside the results set.
           If middle_only is set to 1, it will only print the middle box information (beg/netx/prev/end/etc) links.
           This is suitable for displaying navigation links at the bottom of the search results page.

        Parameters:
          - 'ln' *string* - The language to display
          - 'middle_only' *bool* - Only display parts of the interface
          - 'collection' *string* - the collection name
          - 'collection_name' *string* - the i18nized current collection name
          - 'aas' *bool* - if we display the advanced search interface
          - 'sf' *string* - the currently selected sort format
          - 'so' *string* - the currently selected sort order ("a" or "d")
          - 'rm' *string* - selected ranking method
          - 'rg' *int* - selected results/page
          - 'nb_found' *int* - number of results found
          - 'of' *string* - the selected output format
          - 'ot' *string* - hidden values
          - 'p' *string* - Current search words
          - 'f' *string* - the fields in which the search was done
          - 'f1, f2, f3, m1, m2, m3, p1, p2, p3, op1, op2' *strings* - the search parameters
          - 'jrec' *int* - number of first record on this page
          - 'd1y, d2y, d1m, d2m, d1d, d2d' *int* - the search between dates
          - 'dt' *string* the dates' type (creation date, modification date)
          - 'all_fieldcodes' *array* - all the available fields
          - 'cpu_time' *float* - the time of the query in seconds
        """
        # load the right message language
        _ = gettext_set_language(ln)
        if p2:
            p = p1
            p1 = ''
            p2 = ''
            op1 = ''
            op2 = ''
            aas = 1
        query = {'p': p, 'f': f,
                     'cc': cgi.escape(collection),
                     'sf': sf, 'so': so,
                     'sp': sp, 'rm': rm,
                     'of': of, 'ot': ot,
                     'aas': aas, 'ln': ln,
                     'p1': p1, 'p2': p2, 'p3': p3,
                     'f1': f1, 'f2': f2, 'f3': f3,
                     'm1': m1, 'm2': m2, 'm3': m3,
                     'op1': op1, 'op2': op2,
                     'sc': sc,
                     'd1y': d1y, 'd1m': d1m, 'd1d': d1d,
                     'd2y': d2y, 'd2m': d2m, 'd2d': d2d,
                     'dt': dt,
                     'ln': ln, 'ext': ext or [], 'rg': rg,
        }

        
        if middle_only:
                        
            return self.tmpl_pagination(query_params=query, nb_recs=nb_found, 
                                        recs_per_page=rg, 
                                        jrec=jrec, ln=ln)
        
        sf_labels = {'': _("Creation date"),
                     'title': _("Title"),
                     'author': _("First author"),
                     'reportnumber': _("Report number"),
                     'year': _("Publication year")}
        so_labels = {'a': _("Ascending"),
                     'd': _("Descending")}
        of_labels = {'hb': _("HTML brief"),
                     'hr': _("HTML detailed"),
                     'hm': _("HTML MARC21")}
        out = """
        <div class="results-overview">%(records_found_label)s</div>
        <div class="navigation-bar">
          <div class="group">
            <span>%(sort_label)s</span>
            <ul class="topnav">
              <li class="dropdown"><a href="#">%(selected_sf)s</a>
                <ul class="menu hidden">
                  <li><a href="%(sort_by_cd_url)s">%(sort_by_cd_label)s</a></li>
                  <li><a href="%(sort_by_year_url)s">%(sort_by_year_label)s</a></li>
                  <li><a href="%(sort_by_title_url)s">%(sort_by_title_label)s</a></li>
                  <li><a href="%(sort_by_author_url)s">%(sort_by_author_label)s</a></li>
                </ul>
              </li>
              <li class="dropdown"><a href="#">%(selected_so)s</a>
                <ul class="menu hidden">
                  <li><a href="%(sort_order_asc_url)s">%(sort_order_asc_label)s</a></li>
                  <li><a href="%(sort_order_desc_url)s">%(sort_order_desc_label)s</a></li>
                </ul>
              </li>
            </ul>
          </div>
          <div class="group">
            <span>Afficher</span>
            <ul class="topnav">
              <li class="dropdown"><a href="#">%(selected_rg)s %(results)s</a>
                <ul class="menu hidden">
                  <li><a href="%(nb_results_url)s&amp;rg=10">10 %(results)s</a></li>
                  <li><a href="%(nb_results_url)s&amp;rg=25">25 %(results)s</a></li>
                  <li><a href="%(nb_results_url)s&amp;rg=50">50 %(results)s</a></li>
                  <li><a href="%(nb_results_url)s&amp;rg=100">100 %(results)s</a></li>
                  <li><a href="%(nb_results_url)s&amp;rg=250">250 %(results)s</a></li>
                  <li><a href="%(nb_results_url)s&amp;rg=500">500 %(results)s</a></li>
                </ul>
              </li>
              <li class="dropdown"><a href="#">%(selected_of)s</a>
                <ul class="menu hidden">
                  <li><a href="%(format_hb_url)s">%(format_hb_label)s</a></li>
                  <li><a href="%(format_hr_url)s">%(format_hr_label)s</a></li>
                  <li><a href="%(format_hm_url)s">%(format_hm_label)s</a></li>
                </ul>
              </li>
            </ul>
          </div>
        </div>
        <a name="%(collection_id)s"></a>""" 
        return out % {'records_found_label': _("%s records found") % self.tmpl_nice_number(nb_found, ln),
                      'sort_label': _("Sort by"),
                      'selected_sf': sf_labels.get(sf, sf) ,
                      'collection_id': collection_id,
                      'sort_by_cd_url': self.build_search_url(query, sf=''),
                      'sort_by_cd_label': sf_labels.get(''),
                      'sort_by_year_url': self.build_search_url(query, sf='year'),
                      'sort_by_year_label': sf_labels.get('year'),
                      'sort_by_title_url': self.build_search_url(query, sf='title'),
                      'sort_by_title_label': sf_labels.get('title'),
                      'sort_by_author_url': self.build_search_url(query, sf='author'),
                      'sort_by_author_label': sf_labels.get('author'),
                      'selected_so': so_labels.get(so, so) ,
                      'sort_order_asc_url': self.build_search_url(query, so='a'),
                      'sort_order_asc_label': so_labels.get('a'),
                      'sort_order_desc_url': self.build_search_url(query, so='d'),
                      'sort_order_desc_label': so_labels.get('d'),
                      'selected_rg': rg,
                      'results': _("results"),
                      'nb_results_url': self.build_search_url(query),
                      'selected_of': of_labels.get(of.lower(), of),
                      'format_hb_url': self.build_search_url(query, of='hb'),
                      'format_hb_label': of_labels.get('hb'),
                      'format_hr_url': self.build_search_url(query, of='hr'),
                      'format_hr_label': of_labels.get('hr'),
                      'format_hm_url': self.build_search_url(query, of='hm'),
                      'format_hm_label': of_labels.get('hm'),
                      }
        
    
    def tmpl_record_format_htmlbrief_header(self, ln):
        """EPFL
        Returns the header of the search results list when output
        is html brief. Note that this function is called for each collection
        results when 'split by collection' is enabled.

        See also: tmpl_record_format_htmlbrief_footer,
                  tmpl_record_format_htmlbrief_body

        Parameters:

          - 'ln' *string* - The language to display

        """

        # load the right message language
        _ = gettext_set_language(ln)
        out = """
            <ul class="infoscience_export">"""
        return out

    def tmpl_record_format_htmlbrief_footer(self, ln, display_add_to_basket=True):
        """EPFL
        Returns the footer of the search results list when output
        is html brief. Note that this function is called for each collection
        results when 'split by collection' is enabled.

        See also: tmpl_record_format_htmlbrief_header(..),
                  tmpl_record_format_htmlbrief_body(..)

        Parameters:

          - 'ln' *string* - The language to display
          - 'display_add_to_basket' *bool* - whether to display Add-to-basket button
        """
        # load the right message language
        _ = gettext_set_language(ln)
        out = """
            </ul>
        """
        return out

    def tmpl_record_format_htmlbrief_body(self, ln, recid,
                                          row_number, relevance,
                                          record, relevances_prologue,
                                          relevances_epilogue,
                                          display_add_to_basket=True):
        """
        EPFL
        Returns the html brief format of one record. Used in the
        search results list for each record.
        See also: tmpl_record_format_htmlbrief_header(..),
                  tmpl_record_format_htmlbrief_footer(..)

        Parameters:
          - 'ln' *string* - The language to display
          - 'row_number' *int* - The position of this record in the list
          - 'recid' *int* - The recID
          - 'relevance' *string* - The relevance of the record
          - 'record' *string* - The formatted record
          - 'relevances_prologue' *string* - HTML code to prepend the relevance indicator
          - 'relevances_epilogue' *string* - HTML code to append to the relevance indicator (used mostly for formatting)
        """
        # load the right message language
        _ = gettext_set_language(ln)
        tmpl = """
              <li class="infoscience_record">
                <div class="infoscience_number">
                  %(number)s.
                </div>              
                <div class="infoscience_data">
                  <abbr class="unapi-id" title="%(recid)s"></abbr>
                  %(record)s
                </div>
              </li>"""
             
        if False: # TODO: put this feature on when interface is ready to handle checkboxes... #display_add_to_basket:
            tmpl = """
              <li class="infoscience_record infoscience_record_bulleted">
                <div class="infoscience_bullet"><input name="recid" type="checkbox" value="%(recid)s" /></div>
                <div class="infoscience_number">
                  %(number)s.
                </div>                   
                <div class="infoscience_data">
                  <abbr class="unapi-id" title="%(recid)s"></abbr>
                  %(record)s
                </div>
              </li>"""
                
        return tmpl % {'recid': recid,
                      'number': row_number,
                      'record': record}


    def tmpl_print_results_overview(self, ln, results_final_nb_total, cpu_time, results_final_nb, colls, ec, hosted_colls_potential_results_p=False):
        """Prints results overview box with links to particular collections below.

        Parameters:

          - 'ln' *string* - The language to display

          - 'results_final_nb_total' *int* - The total number of hits for the query

          - 'colls' *array* - The collections with hits, in the format:

          - 'coll[code]' *string* - The code of the collection (canonical name)

          - 'coll[name]' *string* - The display name of the collection

          - 'results_final_nb' *array* - The number of hits, indexed by the collection codes:

          - 'cpu_time' *string* - The time the query took

          - 'url_args' *string* - The rest of the search query

          - 'ec' *array* - selected external collections

          - 'hosted_colls_potential_results_p' *boolean* - check if there are any hosted collections searches
                                                    that timed out during the pre-search
        """

        if len(colls) == 1 and not ec:
            # if one collection only and no external collections, print nothing:
            return ""

        # load the right message language
        _ = gettext_set_language(ln)

        # first find total number of hits:
        # if there were no hosted collections that timed out during the pre-search print out the exact number of records found
        if not hosted_colls_potential_results_p:
            out = """<table class="searchresultsbox">
                    <thead><tr><th class="searchresultsboxheader">%(founds)s</th></tr></thead>
                    <tbody><tr><td class="searchresultsboxbody"> """ % {
                    'founds' : _("%(x_fmt_open)sResults overview:%(x_fmt_close)s Found %(x_nb_records)s records in %(x_nb_seconds)s seconds.") %\
                    {'x_fmt_open': '<strong>',
                     'x_fmt_close': '</strong>',
                     'x_nb_records': '<strong>' + self.tmpl_nice_number(results_final_nb_total, ln) + '</strong>',
                     'x_nb_seconds': '%.2f' % cpu_time}
                  }
        # if there were (only) hosted_collections that timed out during the pre-search print out a fuzzier message
        else:
            if results_final_nb_total == 0:
                out = """<table class="searchresultsbox">
                        <thead><tr><th class="searchresultsboxheader">%(founds)s</th></tr></thead>
                        <tbody><tr><td class="searchresultsboxbody"> """ % {
                        'founds' : _("%(x_fmt_open)sResults overview%(x_fmt_close)s") %\
                        {'x_fmt_open': '<strong>',
                         'x_fmt_close': '</strong>'}
                      }
            elif results_final_nb_total > 0:
                out = """<table class="searchresultsbox">
                        <thead><tr><th class="searchresultsboxheader">%(founds)s</th></tr></thead>
                        <tbody><tr><td class="searchresultsboxbody"> """ % {
                        'founds' : _("%(x_fmt_open)sResults overview:%(x_fmt_close)s Found at least %(x_nb_records)s records in %(x_nb_seconds)s seconds.") %\
                        {'x_fmt_open': '<strong>',
                         'x_fmt_close': '</strong>',
                         'x_nb_records': '<strong>' + self.tmpl_nice_number(results_final_nb_total, ln) + '</strong>',
                         'x_nb_seconds': '%.2f' % cpu_time}
                      }
        # then print hits per collection:
        for coll in colls:
            if results_final_nb.has_key(coll['code']) and results_final_nb[coll['code']] > 0:
                out += """
                      <strong><a href="#%(coll)s">%(coll_name)s</a></strong>, <a href="#%(coll)s">%(number)s</a><br />""" % \
                                      {'coll' : coll['id'],
                                       'coll_name' : cgi.escape(coll['name']),
                                       'number' : _("%s records found") % \
                                       ('<strong>' + self.tmpl_nice_number(results_final_nb[coll['code']], ln) + '</strong>')}
            # the following is used for hosted collections that have timed out,
            # i.e. for which we don't know the exact number of results yet.
            elif results_final_nb.has_key(coll['code']) and results_final_nb[coll['code']] == -963:
                out += """
                      <strong><a href="#%(coll)s">%(coll_name)s</a></strong><br />""" % \
                                      {'coll' : coll['id'],
                                       'coll_name' : cgi.escape(coll['name']),
                                       'number' : _("%s records found") % \
                                       ('<strong>' + self.tmpl_nice_number(results_final_nb[coll['code']], ln) + '</strong>')}
        out += "</td></tr></tbody></table>"
        return out


    def tmpl_print_searchresultbox(self, header, body):
        """print a nicely formatted box for search results """
        #_ = gettext_set_language(ln)

        # first find total number of hits:
        out = '<table class="searchresultsbox"><thead><tr><th class="searchresultsboxheader">'+header+'</th></tr></thead><tbody><tr><td class="searchresultsboxbody">'+body+'</td></tr></tbody></table>'
        return out


    def tmpl_search_no_boolean_hits(self, ln, nearestterms):
        """No hits found, proposes alternative boolean queries

        Parameters:

          - 'ln' *string* - The language to display

          - 'nearestterms' *array* - Parts of the interface to display, in the format:

          - 'nearestterms[nbhits]' *int* - The resulting number of hits

          - 'nearestterms[url_args]' *string* - The search parameters

          - 'nearestterms[p]' *string* - The search terms

        """

        # load the right message language
        _ = gettext_set_language(ln)

        out = _("Boolean query returned no hits. Please combine your search terms differently.")

        out += '''<blockquote><table class="nearesttermsbox" cellpadding="0" cellspacing="0" border="0">'''
        for term, hits, argd in nearestterms:
            out += '''\
            <tr>
              <td class="nearesttermsboxbody" align="right">%(hits)s</td>
              <td class="nearesttermsboxbody" width="15">&nbsp;</td>
              <td class="nearesttermsboxbody" align="left">
                %(link)s
              </td>
            </tr>''' % {'hits' : hits,
                        'link': create_html_link(self.build_search_url(argd),
                                                 {}, cgi.escape(term),
                                                 {'class': "nearestterms"})}
        out += """</table></blockquote>"""
        return out

    def tmpl_similar_author_names(self, authors, ln):
        """No hits found, proposes alternative boolean queries

        Parameters:

          - 'authors': a list of (name, hits) tuples
          - 'ln' *string* - The language to display
        """

        # load the right message language
        _ = gettext_set_language(ln)

        out = '''<a name="googlebox"></a>
                 <table class="googlebox"><tr><th colspan="2" class="googleboxheader">%(similar)s</th></tr>''' % {
                'similar' : _("See also: similar author names")
              }
        for author, hits in authors:
            out += '''\
            <tr>
              <td class="googleboxbody">%(nb)d</td>
              <td class="googleboxbody">%(link)s</td>
            </tr>''' % {'link': create_html_link(
                                    self.build_search_url(p=author,
                                                          f='author',
                                                          ln=ln),
                                    {}, cgi.escape(author), {'class':"google"}),
                        'nb' : hits}

        out += """</table>"""

        return out

    def tmpl_print_record_list_for_similarity_boxen(self, title, recID_score_list, ln=CFG_SITE_LANG):
        """Print list of records in the "hs" (HTML Similarity) format for similarity boxes.
           RECID_SCORE_LIST is a list of (recID1, score1), (recID2, score2), etc.
        """

        from invenio.search_engine import print_record, record_public_p

        recID_score_list_to_be_printed = []

        # firstly find 5 first public records to print:
        nb_records_to_be_printed = 0
        nb_records_seen = 0
        while nb_records_to_be_printed < 5 and nb_records_seen < len(recID_score_list) and nb_records_seen < 50:
            # looking through first 50 records only, picking first 5 public ones
            (recID, score) = recID_score_list[nb_records_seen]
            nb_records_seen += 1
            if record_public_p(recID):
                nb_records_to_be_printed += 1
                recID_score_list_to_be_printed.append([recID, score])

        # secondly print them:
        out = '''
        <table><tr>
         <td>
          <table><tr><td class="blocknote">%(title)s</td></tr></table>
         </td>
         </tr>
         <tr>
          <td><table>
        ''' % { 'title': cgi.escape(title) }
        for recid, score in recID_score_list_to_be_printed:
            out += '''
            <tr><td><font class="rankscoreinfo"><a>(%(score)s)&nbsp;</a></font><small>&nbsp;%(info)s</small></td></tr>''' % {
                'score': score,
                'info' : print_record(recid, format="hs", ln=ln),
                }

        out += """</table></td></tr></table> """
        return out

    def tmpl_print_record_brief_links(self, ln, recID, sf='', so='d', sp='', rm='', user_info=None):
        """
        EPFL
        Displays links for brief record on-the-fly
        Parameters:
          - 'ln' *string* - The language to display
          - 'recID' *int* - The record id
        """
        # load the right message language
        
        _ = gettext_set_language(ln)
        
        links = []
        #links.append(create_html_link(self.build_search_url(p="recid:%d" % recID, rm="wrd", ln=ln),
        #                              {}, _("Similar records"),
        #                              {'class': "infoscience_link_similar"}))
        if user_info and user_info.get('guest', '1') == '0':
            links.append(create_html_link('/yourbaskets/add', {'recid': recID, 'ln': ln},
                                          _("Add to my collections"), {'class': "infoscience_link_basket modal-opener", 'rel': '#basket_modal'}))
        out = '<span class="infoscience_links">%s</span>'
        return out % ''.join(links)

    def tmpl_collection_not_found_page_body(self, colname, ln=CFG_SITE_LANG):
        """
        Create page body for cases when unexisting collection was asked for.
        """
        _ = gettext_set_language(ln)
        out = """<h1>%(title)s</h1>
                 <p>%(sorry)s</p>
                 <p>%(you_may_want)s</p>
              """ % { 'title': self.tmpl_collection_not_found_page_title(colname, ln),
                      'sorry': _("Sorry, collection %s does not seem to exist.") % \
                                ('<strong>' + cgi.escape(colname) + '</strong>'),
                      'you_may_want': _("You may want to start browsing from %s.") % \
                                 ('<a href="' + CFG_SITE_URL + '?ln=' + ln + '">' + \
                                        cgi.escape(CFG_SITE_NAME_INTL.get(ln, CFG_SITE_NAME)) + '</a>')}
        return out

    def tmpl_alert_rss_teaser_box_for_query(self, id_query, ln, display_email_alert_part=True):
        """
        EPFL
        Propose teaser for setting up this query as alert or RSS feed.

        Parameters:
          - 'id_query' *int* - ID of the query we make teaser for
          - 'ln' *string* - The language to display
          - 'display_email_alert_part' *bool* - whether to display email alert part
        """
        return ''

    def tmpl_detailed_record_metadata(self, recID, ln, format,
                                      content,
                                      creationdate=None,
                                      modificationdate=None):
        """Returns the main detailed page of a record
        Parameters:
          - 'recID' *int* - The ID of the printed record
          - 'ln' *string* - The language to display
          - 'format' *string* - The format in used to print the record
          - 'content' *string* - The main content of the page
          - 'creationdate' *string* - The creation date of the printed record
          - 'modificationdate' *string* - The last modification date of the printed record
        """
        _ = gettext_set_language(ln)
        ## unAPI identifier
        out = '<abbr class="unapi-id" title="%s"></abbr>\n' % recID
        out += content

        return out

    def tmpl_record_plots(self, recID, ln):
        """
          Displays little tables containing the images and captions contained in the specified document.

        Parameters:

          - 'recID' *int* - The ID of the printed record

          - 'ln' *string* - The language to display
        """
        from invenio.search_engine import get_record
        from invenio.bibrecord import field_get_subfield_values
        from invenio.bibrecord import record_get_field_instances
        _ = gettext_set_language(ln)

        out = ''

        rec = get_record(recID)
        flds = record_get_field_instances(rec, '856', '4')

        images = []

        for fld in flds:
            image = field_get_subfield_values(fld, 'u')
            caption = field_get_subfield_values(fld, 'y')

            if type(image) == list and len(image) > 0:
                image = image[0]
            else:
                continue
            if type(caption) == list and len(caption) > 0:
                caption = caption[0]
            else:
                continue

            if not image.endswith('.png'):
                # huh?
                continue

            if len(caption) >= 5:
                images.append((int(caption[:5]), image, caption[5:]))
            else:
                # we don't have any idea of the order... just put it on
                images.append(99999, image, caption)

        images = sorted(images, key=lambda x: x[0])

        for (index, image, caption) in images:
            # let's put everything in nice little subtables with the image
            # next to the caption
            out = out + '<table width="95%" style="display: inline;">' +\
                 '<tr><td width="66%"><a name="' + str(index) + '" ' +\
                 'href="' + image + '">' +\
                 '<img src="' + image + '" width="95%"/></a></td>' +\
                 '<td width="33%">' + caption + '</td></tr>' +\
                 '</table>'

        out = out + '<br /><br />'

        return out


    def tmpl_detailed_record_statistics(self, recID, ln,
                                        downloadsimilarity,
                                        downloadhistory, viewsimilarity):
        """Returns the statistics page of a record

        Parameters:

          - 'recID' *int* - The ID of the printed record

          - 'ln' *string* - The language to display

          - downloadsimilarity *string* - downloadsimilarity box

          - downloadhistory *string* - downloadhistory box

          - viewsimilarity *string* - viewsimilarity box

        """
        # load the right message language
        _ = gettext_set_language(ln)

        out = ''

        if CFG_BIBRANK_SHOW_DOWNLOAD_STATS and downloadsimilarity is not None:
            similar = self.tmpl_print_record_list_for_similarity_boxen (
                _("People who downloaded this document also downloaded:"), downloadsimilarity, ln)

            out = '<table>'
            out += '''
                    <tr><td>%(graph)s</td></tr>
                    <tr><td>%(similar)s</td></tr>
                    ''' % { 'siteurl': CFG_SITE_URL,   'recid': recID, 'ln': ln,
                             'similar': similar, 'more': _("more"),
                             'graph': downloadsimilarity
                             }

            out += '</table>'
            out +=  '<br />'

        if CFG_BIBRANK_SHOW_READING_STATS and viewsimilarity is not None:
            out += self.tmpl_print_record_list_for_similarity_boxen (
                _("People who viewed this page also viewed:"), viewsimilarity, ln)

        if CFG_BIBRANK_SHOW_DOWNLOAD_GRAPHS and downloadhistory is not None:
            out += downloadhistory + '<br />'

        return out



    def tmpl_author_information(self, req, pubs, authorname, num_downloads, aff_pubdict,
                                citedbylist, kwtuples, authors, vtuples, ln):
        """Prints stuff about the author given as authorname.
           1. Author name + his/her institutes. Each institute I has a link
              to papers where the auhtor has I as institute.
           2. Publications, number: link to search by author.
           3. Keywords
           4. Author collabs
           5. Publication venues like journals
           The parameters are data structures needed to produce 1-6, as follows:
           req - request
           pubs - list of recids, probably the records that have the author as an author
           authorname - evident
           num_downloads - evident
           aff_pubdict - a dictionary where keys are inst names and values lists of recordids
           citedbylist - list of recs that cite pubs
           kwtuples - keyword tuples like ('HIGGS BOSON',[3,4]) where 3 and 4 are recids
           authors - a list of authors that have collaborated with authorname
        """
        from invenio.search_engine import perform_request_search
        _ = gettext_set_language(ln)
        #make a authoraff string that looks like CERN (1), Caltech (2) etc
        authoraff = ""
        aff_pubdict_keys = aff_pubdict.keys()
        aff_pubdict_keys.sort(lambda x, y: cmp(len(aff_pubdict[y]), len(aff_pubdict[x])))
        for a in aff_pubdict_keys:
            recids = "+or+".join(map(str, aff_pubdict[a]))
            print_a = a
            if (print_a == ' '):
                print_a = _("unknown")
            if authoraff:
                authoraff += '<br>'
            authoraff += "<a href=\"../search?f=recid&p="+recids+"\">"+print_a+' ('+str(len(aff_pubdict[a]))+")</a>"

        #print a "general" banner about the author
        req.write("<h1>" + authorname + "</h1>")

        # print papers:
        searchstr = create_html_link(self.build_search_url(p=authorname,
                                     f='exactauthor'),
                                     {}, "All papers ("+str(len(pubs))+")",)
        line1 = "<strong>" + _("Papers:") + "</strong>"
        line2 = searchstr
        if CFG_BIBRANK_SHOW_DOWNLOAD_STATS and num_downloads:
            line2 += " ("+_("downloaded")+" "
            line2 += str(num_downloads)+" "+_("times")+")"
        if CFG_INSPIRE_SITE:
            CFG_COLLS = ['Book',
                         'Conference',
                         'Introductory',
                         'Lectures',
                         'Preprint',
                         'Published',
                         'Report',
                         'Review',
                         'Thesis']
        else:
            CFG_COLLS = ['Article',
                         'Book',
                         'Preprint',]
        collsd = {}
        for coll in CFG_COLLS:
            coll_num_papers = len(intbitset(pubs) & intbitset(perform_request_search(p="collection:"+coll)))
            if coll_num_papers:
                collsd[coll] =  coll_num_papers
        colls = collsd.keys()
        colls.sort(lambda x, y: cmp(collsd[y], collsd[x])) # sort by number of papers
        for coll in colls:
            line2 += "<br>" + create_html_link(self.build_search_url(p='exactauthor:"' + authorname + '" ' + \
                                                                     'collection:' + coll),
                                                   {}, coll + " ("+str(collsd[coll])+")",)
        banner = self.tmpl_print_searchresultbox(line1, line2)


        req.write("<table width=80%><tr valign=top><td>")
        req.write(banner)
        req.write("</td><td>&nbsp;</td>")

        #print affiliations
        line1 = "<strong>" + _("Affiliations:") + "</strong>"
        line2 = authoraff
        req.write("<td>")
        req.write(self.tmpl_print_searchresultbox(line1, line2))
        req.write("</td></tr>")

        # print frequent keywords:
        keywstr = ""
        if (kwtuples):
            for (kw, freq) in kwtuples:
                if keywstr:
                    keywstr += '<br>'
                #create a link in author=x, keyword=y
                searchstr = create_html_link(self.build_search_url(
                                                p='exactauthor:"' + authorname + '" ' +
                                                  'keyword:"' + kw + '"'),
                                                {}, kw+" ("+str(freq)+")",)
                keywstr = keywstr+" "+searchstr
        else: keywstr += 'No Keywords found'
        banner = self.tmpl_print_searchresultbox("<strong>" + _("Frequent keywords:") + "</strong>", keywstr)
        req.write("<tr valign=top><td>")
        req.write(banner)
        req.write("</td><td>&nbsp;</td>")


        # print frequent co-authors:
        collabstr = ""
        if (authors):
            for c in authors:
                c = c.strip()
                if collabstr:
                    collabstr += '<br>'
                #do not add this person him/herself in the list
                cUP = c.upper()
                authornameUP = authorname.upper()
                if not cUP == authornameUP:
                    commpubs = intbitset(pubs) & intbitset(perform_request_search(p="exactauthor:\"%s\" exactauthor:\"%s\"" % (authorname, c)))
                    collabstr = collabstr + create_html_link(self.build_search_url(p='exactauthor:"' + authorname + '" exactauthor:"' + c + '"' ),
                                                              {}, c + " (" + str(len(commpubs)) + ")",)
        else: collabstr += 'None'
        banner = self.tmpl_print_searchresultbox("<strong>" + _("Frequent co-authors:") + "</strong>", collabstr)
        req.write("<td>")
        req.write(banner)
        req.write("</td></tr></table>")

        # print frequently publishes in journals:
        #if (vtuples):
        #    pubinfo = ""
        #    for t in vtuples:
        #        (journal, num) = t
        #        pubinfo += create_html_link(self.build_search_url(p='exactauthor:"' + authorname + '" ' + \
        #                                                          'journal:"' + journal + '"'),
        #                                           {}, journal + " ("+str(num)+")<br/>")
        #    banner = self.tmpl_print_searchresultbox("<strong>" + _("Frequently publishes in:") + "<strong>", pubinfo)
        #    req.write(banner)



        # print citations:
        if len(citedbylist):
            line1 = "<strong>" + _("Citations:") + "</strong>"
            line2 = ""
            req.write(self.tmpl_print_searchresultbox(line1, line2))
            # they will be printed after that


