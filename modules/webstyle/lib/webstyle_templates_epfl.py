# -*- coding: utf-8 -*-
"""
EPFL templates.
Webstyle handles header, general page design and main navigation.
"""
import os
import urllib, cgi
from datetime import datetime

from invenio.config import CFG_SITE_LANG, CFG_SITE_URL, CFG_SITE_SECURE_URL, CFG_SITE_NAME, CFG_SITE_NAME_INTL, CFG_SITE_SUPPORT_EMAIL, CFG_VERSION
from invenio.messages import gettext_set_language
from invenio.urlutils import make_canonical_urlargd, create_html_link
from invenio.webuser import collect_user_info
from invenio import webstyle_templates
from xml.sax import saxutils

class Template(webstyle_templates.Template):
    """EPFL template"""
    
    def tmpl_pageheader(self, req, ln=CFG_SITE_LANG, headertitle="",
                        description="", keywords="", userinfobox="",
                        useractivities_menu="", adminactivities_menu="",
                        navtrailbox="", pageheaderadd="", uid=0,
                        secure_page_p=0, navmenuid="admin", metaheaderadd="",
                        rssurl='', body_css_classes=None):
        if secure_page_p:
            external_scripts = """
    <link href="https://www.epfl.ch/css/epfl.css" media="all" rel="stylesheet" type="text/css" />
    <link href="https://www.epfl.ch/css/applications.css" media="all" rel="stylesheet" type="text/css" />
    <script type="text/javascript" src="https://www.epfl.ch/js/jquery-epfl.min.js"></script>
    <script type="text/javascript" src="https://www.epfl.ch/js/globalnav.js"></script>"""
        else:
            # secure_page_p seems to be empty all the time... Therefore, we
            # return https all the time.
            external_scripts = """
    <link href="https://www.epfl.ch/css/epfl.css" media="all" rel="stylesheet" type="text/css" />
    <link href="https://www.epfl.ch/css/applications.css" media="all" rel="stylesheet" type="text/css" />
    <script type="text/javascript" src="https://www.epfl.ch/js/jquery-epfl.min.js"></script>
    <script type="text/javascript" src="https://www.epfl.ch/js/globalnav.js"></script>"""
        
        rss = ''
        if rssurl:
            rss = '<link rel="alternate" type="application/rss+xml" title="%s RSS" href="%s" />' % (CFG_SITE_NAME_INTL.get(ln, CFG_SITE_NAME), rssurl)

        out = """\
<!DOCTYPE html PUBLIC "-/W3C/DTD XHTML 1.0 Transitional/EN" 
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="%(ln)s" xml:lang="%(ln)s">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>%(title)s</title>
    <link rev="made" href="mailto:%(sitesupportemail)s" />
    %(rss)s
    <link rel="search" type="application/opensearchdescription+xml" href="%(siteurl)s/opensearchdescription" title="%(sitename)s" />
    <link rel="unapi-server" type="application/xml" title="unAPI" href="%(unAPIurl)s" />

%(external_scripts)s

    <link href="/media/css/invenio_epfl.css" media="all" rel="stylesheet" type="text/css" />    
    <script type="text/javascript" src="/media/js/invenio-epfl.js"></script>
%(signature)s
%(metaheaderadd)s
  </head>
  <body%(body_css_classes)s lang="%(ln)s">
%(header)s
    <div id="main-content">
%(breadcrumbs)s
%(language)s
      <div class="clear"></div>
      <p class="h1"><a href="/?ln=%(ln)s">Infoscience</a><!-- Publications <acronym title="École Polytechnique Fédérale de Lausanne" class="local-color-text">EPFL</acronym>--></p>
      %(message)s
%(navigation)s
""" % {'signature': epfl_header_version(),
       'body_css_classes' : body_css_classes and ' class="%s"' % ' '.join(body_css_classes) or '',
       'ln' : ln,
       'sitename': CFG_SITE_NAME_INTL.get(ln, CFG_SITE_NAME),
       'sitesupportemail': CFG_SITE_SUPPORT_EMAIL,
       'siteurl': CFG_SITE_URL,
       'rss': rss,
       'unAPIurl': '%s/unapi' % CFG_SITE_URL,
       'metaheaderadd': metaheaderadd,
       'header': epfl_header(ln), 
       'title': saxutils.unescape(headertitle),
       'breadcrumbs': navtrailbox,
       'language': self.tmpl_language_selection_box(req, ln),
       'navigation': self.get_navigation(req, useractivities_menu, adminactivities_menu, navmenuid, ln),
       'external_scripts': external_scripts,
       'message': '' #self.maintenance_warning(ln),
        }
        return out

    def maintenance_warning(self, ln=CFG_SITE_LANG):
     return """
      <div style="padding: 8px;border: 1px solid  #ddcccc; font-size:1.1em; margin-bottom: 8px;" >
      <img src="/media/img/warning.png" height="64" width="64" style="float: left; margin-right:8px;">
      
      <h3>%(warning)s</h3><p>%(message)s</p></div>""" % {       
        'warning': ln=='en' and 'Maintenance notice' or 'Avis de maintenance',
        'message': ln=='en' and "Due to the moving of its main server, Infoscience will be set in read-only mode from Wednesday, 20th at 18:00 to Friday 22nd at 9:00. We apologize for the inconvenience. Exports of publication lists on your web sites will not be affected." or "Infoscience ne sera accessible qu'en lecture entre le mercredi 20 à 18h et le vendredi 22 à 9h à cause d'un déplacement de serveur. Nous vous prions de nous excuser pour les désagréments. Les exports de listes de publications vers vos sites web continueront de fonctionner."}
         
    

    def tmpl_pagefooter(self, req=None, ln=CFG_SITE_LANG, lastupdated=None, pagefooteradd="", ):
        _ = gettext_set_language(ln)

        out = """
    <div class="clear"></div>
    <div id="footer">
      <ul>
        <li><a href="http://help-infoscience.epfl.ch/%(about)s">%(about_label)s</a></li>
        <li><a href="mailto:infoscience@epfl.ch">%(contact_label)s</a></li>
        <li><a href="http://www.epfl.ch/accessibility.%(ln)s">%(accessibility_label)s</a></li>
        <li class="copyright">&copy; 2004-%(year)s EPFL tous droits réservés</li>
        <li>Powered by <a href="http://invenio-software.org">Invenio</a></li>
        <li class="login">%(login_link)s</li>
      </ul>
    </div>
%(pagefooteradd)s
  <script type="text/javascript">
  
      var _gaq = _gaq || [];
      _gaq.push(['_setAccount', 'UA-1830336-6']);
      _gaq.push(['_setDomainName', 'infoscience.epfl.ch']);
      
      _gaq.push(['_trackPageview']);

      (function() {
        var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
      })();
  
    </script>
""" % {
                     'about': ln=='fr' and 'a-propos' or 'about',
                     'about_label': _("About Infoscience"),
                     'contact_label': _("Contact"),
                     'accessibility_label': _("Accessibility"), 
                     'login_link': self.get_login_link(req, ln),
                     'ln': ln,
                     'pagefooteradd': pagefooteradd,
                     'year': datetime.now().year,
                     'version': CFG_VERSION,
                }
        return out
    
    def get_login_link(self, req, ln=CFG_SITE_LANG):
        _ = gettext_set_language(ln)
        if req:
            if req.subprocess_env.has_key('HTTPS') \
                and req.subprocess_env['HTTPS'] == 'on':
                    url_referer = CFG_SITE_SECURE_URL + req.unparsed_uri
            else:
                url_referer = CFG_SITE_URL + req.unparsed_uri
            if '/youraccount/logout' in url_referer:
                url_referer = ''
        else:
            url_referer = CFG_SITE_URL
        
        user_info = collect_user_info(req)
        if int(user_info.get('guest', '1')):
            login_link = '<a href="%(sitesecureurl)s/youraccount/login?ln=%(ln)s%(referer)s">%(login)s</a>' % {
                        'sitesecureurl': CFG_SITE_SECURE_URL,
                        'ln' : ln,
                        'referer' : url_referer and ('&amp;referer=%s' % urllib.quote(url_referer)) or '',
                        'login' : _('Login')
                        }
        else:
            login_link = """<a href="/youraccount/logout?ln=%(ln)s">%(logout)s</a>""" % {'ln' : ln, 
                                                                                         'logout' : _("Logout (%(username)s)") % {'username': user_info.get('external_uid', [None])[0] or user_info.get('email')}
                                                                                         }
        return login_link

        
    
    def tmpl_page(self, req=None, ln=CFG_SITE_LANG, description="",
                  keywords="", userinfobox="", useractivities_menu="",
                  adminactivities_menu="", navtrailbox="",
                  pageheaderadd="", boxlefttop="", boxlefttopadd="",
                  boxleftbottom="", boxleftbottomadd="",
                  boxrighttop="", boxrighttopadd="",
                  boxrightbottom="", boxrightbottomadd="",
                  titleprologue="", title="", titleepilogue="",
                  body="", lastupdated=None, pagefooteradd="", uid=0,
                  secure_page_p=0, navmenuid="", metaheaderadd="",
                  rssurl=CFG_SITE_URL+"/rss",
                  show_title_p=True, body_css_classes=None):

        """Creates a complete page
           Parameters:
          - 'ln' *string* - The language to display
          - 'description' *string* - description goes to the metadata in the header of the HTML page
          - 'keywords' *string* - keywords goes to the metadata in the header of the HTML page
          - 'userinfobox' *string* - the HTML code for the user information box
          - 'useractivities_menu' *string* - the HTML code for the user activities menu
          - 'adminactivities_menu' *string* - the HTML code for the admin activities menu
          - 'navtrailbox' *string* - the HTML code for the navigation trail box
          - 'pageheaderadd' *string* - additional page header HTML code
          - 'boxlefttop' *string* - left-top box HTML code
          - 'boxlefttopadd' *string* - additional left-top box HTML code
          - 'boxleftbottom' *string* - left-bottom box HTML code
          - 'boxleftbottomadd' *string* - additional left-bottom box HTML code
          - 'boxrighttop' *string* - right-top box HTML code
          - 'boxrighttopadd' *string* - additional right-top box HTML code
          - 'boxrightbottom' *string* - right-bottom box HTML code
          - 'boxrightbottomadd' *string* - additional right-bottom box HTML code
          - 'title' *string* - the title of the page
          - 'titleprologue' *string* - what to print before page title
          - 'titleepilogue' *string* - what to print after page title
          - 'body' *string* - the body of the page
          - 'lastupdated' *string* - when the page was last updated
          - 'uid' *int* - user ID
          - 'pagefooteradd' *string* - additional page footer HTML code
          - 'secure_page_p' *int* (0 or 1) - are we to use HTTPS friendly page elements or not?
          - 'navmenuid' *string* - the id of the navigation item to highlight for this page
          - 'metaheaderadd' *string* - list of further tags to add to the <HEAD></HEAD> part of the page
          - 'rssurl' *string* - the url of the RSS feed for this page
          - 'show_title_p' *int* (0 or 1) - do we display the page title in the body of the page?
          - 'body_css_classes' *list* - list of classes to add to the body tag
           Output:
          - HTML code of the page
        """
        # load the right message language
        _ = gettext_set_language(ln)
        if title == CFG_SITE_NAME:
            title = _("Infoscience: Scientific publications of EPFL")
        else:
            title = title + ' - Infoscience'
        
        header = self.tmpl_pageheader(req,
                                   ln = ln,
                                   headertitle = title,
                                   description = description,
                                   keywords = keywords,
                                   metaheaderadd = metaheaderadd,
                                   userinfobox = userinfobox,
                                   navtrailbox = navtrailbox,
                                   pageheaderadd = pageheaderadd,
                                   secure_page_p = secure_page_p,
                                   navmenuid=navmenuid,
                                   rssurl=rssurl,
                                   body_css_classes=body_css_classes,
                                   useractivities_menu=useractivities_menu,
                                   adminactivities_menu=adminactivities_menu)
        
        footer = self.tmpl_pagefooter(req, ln=ln, lastupdated=lastupdated, pagefooteradd=pagefooteradd)
        if navmenuid == 'search':
            #IDEE: trouver un moyen de reconnaitre webcoll: navmenuid=search; délégation de content, right col
            #                                  search: navmenuid=search; délégation de content et right-col
            body = body
        
        elif navmenuid == 'yourbaskets':
            body = body
        
        elif navmenuid == 'youralerts':
            body = body
        
        elif navmenuid == '503':
            body = body

        elif boxlefttop or boxlefttopadd or boxleftbottom or boxleftbottomadd or \
           boxrighttop or boxrighttopadd or boxrightbottom or boxrightbottomadd:
            body = """
        <div id="content" class="content">
          <h2>%(title)s</h2>
%(body)s
        </div>
        <div class="right-col">
%(blt)s
%(blta)s
%(blba)s
%(blb)s
%(brt)s
%(brta)s
%(brba)s
%(brb)s
        </div>
        <div class="clear"></div>""" % {'title': title, 'body': body, 'navmenuid':navmenuid,
                     'blt': boxlefttop, 'blta': boxlefttopadd, 
                     'blb': boxleftbottom, 'blba': boxleftbottomadd, 
                     'brt': boxrighttop, 'brta': boxrighttopadd,
                     'brb': boxrightbottom, 'brba': boxrightbottomadd }

        
        else:
            body = """
        <div id="content" class="content fullpage-content">
          <h2>%(title)s</h2>
%(body)s
        </div>
""" % {'title': title, 'body': body, 'navmenuid':navmenuid}
        
        out = """
%(header)s
%(body)s   
%(footer)s
  </body>
</html>
        """ % {'header': header, 
               'title': title,
               'navigation': self.get_navigation(req, useractivities_menu, adminactivities_menu, navmenuid, ln),
               'body': body,
               'footer': footer,
               }
        
        return out
    
    def tmpl_language_selection_box(self, req, language=CFG_SITE_LANG):
        """Take URLARGS and LANGUAGE and return textual language
           selection box for the given page.
           Parameters:
          - 'req' - The mod_python request object
          - 'language' *string* - The selected language
        """
        _ = gettext_set_language(language)
        argd = {}
        if req and req.args:
            argd.update(cgi.parse_qs(req.args))
        
        if language == 'en':
            out = """
      <ul id="languages" title="%s">
        <li class="current">English</li>
        <li><a href="%s">français</a></li>
      </ul>"""
            argd['ln'] = 'fr'
        else:
            out = """
      <ul id="languages" title="%s">
        <li><a href="%s">English</a></li>
        <li class="current">français</li>
      </ul>"""
            argd['ln'] = 'en'
        return out % (_("Choose your language"), 
                      urllib.quote(req.uri, '/:?') + make_canonical_urlargd(argd, {}))
        
    
    def get_navigation(self, req, useractivities_menu='', adminactivities_menu='', navmenuid='', ln=CFG_SITE_LANG):
        _ = gettext_set_language(ln)
        search_menu_cls = ''
        browse_menu_cls = ''
        account_menu_cls = ''
        admin_menu_cls = ''
        if req.uri.strip() == '/' :
            search_menu_cls = '' 
        elif req.uri.startswith('/collection/'):
            browse_menu_cls = 'current'
        elif navmenuid == 'search':
            search_menu_cls = 'current'
        elif navmenuid.startswith('your') or navmenuid == 'personalize':
            account_menu_cls = 'current'
        elif navmenuid in ['stats', 'collection population', 'search frequency', 'search type distribution', 'download frequency', 'custom event', 'custom event help', 'export', 'batchuploader', 'admin']:
            admin_menu_cls = 'current'
            
        if adminactivities_menu:
            admin_menu = """
          <li class="dropdown %(admin_menu_cls)s">
            <a href="http://infoscience.epfl.ch/curator?ln=%(ln)s">Admin</a>
            %(admin_menu)s
          </li>""" % {'admin_menu_cls': admin_menu_cls, 
                      'admin_menu': adminactivities_menu,
                      'ln': ln}
        else:
            admin_menu = ''
        
        if useractivities_menu:
            account_menu = """
          <li class="dropdown %(account_menu_cls)s">
            <a href="%(site_url)s/curator/my_account/profile/?ln=%(ln)s">%(label1)s</a>
            %(account_menu)s
          </li>
          """ % {'label1': _("My account"),
                      'site_url' : CFG_SITE_URL,
                      'account_menu_cls': account_menu_cls, 
                      'account_menu': useractivities_menu,
                      'ln': ln}
        else:
            account_menu = '' 
        
        out = """
        <div id="main-navigation" class="navigation-bar">
        <ul class="topnav">
          <li class="dropdown %(search_menu_cls)s">
            <a href="/?ln=%(ln)s">%(search_label)s</a>
          </li>
          <li class="dropdown %(browse_menu_cls)s">
            <a href="/collection/Infoscience/Research?ln=%(ln)s">%(browse_label)s</a>
            <ul class="menu hidden">
              <li><a href="/collection/Infoscience/Research?ln=%(ln)s">%(by_school)s</a>
                <ul>
                  <li><a href="/collection/Infoscience/Research/ENAC?ln=%(ln)s">%(ENAC)s</a></li>
                  <li><a href="/collection/Infoscience/Research/IC?ln=%(ln)s">%(IC)s</a></li>
                  <li><a href="/collection/Infoscience/Research/SB?ln=%(ln)s">%(SB)s</a></li>
                  <li><a href="/collection/Infoscience/Research/STI?ln=%(ln)s">%(STI)s</a></li>
                  <li><a href="/collection/Infoscience/Research/SV?ln=%(ln)s">%(SV)s</a></li>
                  <li><a href="/collection/Infoscience/Research/CDM?ln=%(ln)s">%(CDM)s</a></li>
                  <li><a href="/collection/Infoscience/Research/CDH?ln=%(ln)s">%(CDH)s</a></li>
                  <li><a href="/collection/Infoscience/Research/ENT?ln=%(ln)s">%(ENT)s</a></li>
                  </ul>
              
              </li>
              <li><a href="/search?ln=%(ln)s&as=1">%(by_doctype)s</a>
                <ul>
                  <li><a href="/collection/Infoscience/Article?ln=%(ln)s">%(ARTICLE)s</a></li>
                  <li><a href="/collection/Infoscience/Conference?ln=%(ln)s">%(CONF)s</a></li>
                  <li><a href="/collection/Infoscience/Thesis?ln=%(ln)s">%(THESIS)s</a></li>
                  <li><a href="/collection/Infoscience/Reports?ln=%(ln)s">%(REPORT)s</a></li>
                </ul>
              </li>
            </ul>
          </li>
          <li class="dropdown">
            <a href="%(secure_domain)s/curator/submit?ln=%(ln)s">%(submit_label)s</a>
          </li>
%(account_menu)s
          <li class="dropdown">
            <a href="http://help-infoscience.epfl.ch">%(help_label)s</a>
            <ul class="menu hidden">
              <li><a href="http://help-infoscience.epfl.ch/%(about_p)s">%(about)s</a></li>
              <li><a href="http://help-infoscience.epfl.ch/%(openaccess_p)s">%(openaccess)s</a></li>
              <li>
                <a href="http://help-infoscience.epfl.ch/%(deposit_p)s">%(submit_label)s</a>
                <ul>
                  <!-- <li><a href="http://help-infoscience.epfl.ch/%(start_p)s">%(start)s</a></li>-->
                  <li><a href="http://help-infoscience.epfl.ch/%(add_p)s">%(add)s</a></li>
                  <li><a href="http://help-infoscience.epfl.ch/%(doctypes_p)s">%(doctypes)s</a></li>
                  <li><a href="http://help-infoscience.epfl.ch/%(status_p)s">%(status)s</a></li>
                </ul>
              </li>
              <li><a href="http://help-infoscience.epfl.ch/%(search_p)s">%(search_label)s</a></li>
              <li>
                <a href="http://help-infoscience.epfl.ch/%(manage_p)s">%(manage)s</a>
                <ul>
                  <li><a href="http://help-infoscience.epfl.ch/%(edit_p)s">%(edit)s</a></li>
                  <li><a href="http://help-infoscience.epfl.ch/%(remove_p)s">%(remove)s</a></li>
                  <li><a href="http://help-infoscience.epfl.ch/%(export_p)s">%(export)s</a></li>
                </ul>
              </li>
              <li>
                <a href="http://help-infoscience.epfl.ch/%(manage_a_p)s">%(manage_a)s</a>
                <ul>
                  <li><a href="http://help-infoscience.epfl.ch/%(basket_p)s">%(basket)s</a></li>
                  <li><a href="http://help-infoscience.epfl.ch/%(people_p)s">%(people)s</a></li>
                </ul>
              </li>
            </ul>
          </li>
%(admin_menu)s
        </ul>
        <div class="clear"></div>
      </div>"""
        return out % { 
                       'secure_domain': CFG_SITE_SECURE_URL, 
                       'search_menu_cls': search_menu_cls, 
                       'browse_menu_cls': browse_menu_cls, 
                       'account_menu_cls': account_menu_cls, 
                       'admin_menu': admin_menu,
                       'account_menu': account_menu,
                       'ln': ln,
                       'search_label': _("Search"),
                       'browse_label': _("Browse"),
                       'by_school': _("Publications by school"),
                       'ENAC': _("ENAC - Architecture, Civil and Environmental Engineering"),
                       'IC': _("I&amp;C - Computer &amp; Communication Sciences"),
                       'SB': _("SB - Basic Sciences"),
                       'STI': _("STI - Engineering"),
                       'SV': _("SV - Life Sciences"),
                       'CDM': _("CDM - Management of Technology"),
                       'CDH': _("CDH - College of Humanities"),
                       'ENT': _("ENT - Transdisciplinary Entities"),
                       'by_doctype': _("Publications by document type"),
                       'ARTICLE': _("Journal Articles"),
                       'CONF': _("Conference Papers"),
                       'THESIS': _("Theses"),
                       'REPORT': _("Reports"),
                       'submit_label': _("Deposit / Publish"),
                       'help_label': _("Help"),
                       'about': _('About Infoscience'),
                       'openaccess': _('Open Access &amp; Copyright'),
                       'start': _('Start using Infoscience'),
                       'add': _('Add a document'),
                       'doctypes': _("Document types"),
                       'status': _("Publication status"),
                       'manage': _("Manage publications"),
                       'edit': _("Edit a publication"),
                       'remove': _("Remove a publication"),
                       'export': _('Export a publication list'),
                       'manage_a': _("Manage my account"),
                       'basket': _("Create a personal collection"),
                       'people': _('Display my publications in people@EPFL'),
                       'about_p': ln=='fr' and 'a-propos' or 'about',
                       'openaccess_p': ln=='fr' and 'libre-acces' or 'open-access',
                       'deposit_p': ln=='fr' and 'deposer' or 'deposit',
                       'start_p': ln=='fr' and 'deposer/demarrer' or 'deposit/start',
                       'add_p': ln=='fr' and 'deposer/nouveau' or 'deposit/new',
                       'doctypes_p': ln=='fr' and 'deposer/types-de-documents' or 'deposit/document-types',
                       'status_p': ln=='fr' and 'deposer/statut' or 'deposit/status',
                       'search_p': ln=='fr' and 'rechercher' or 'search',
                       'manage_p': ln=='fr' and 'gerer-les-publications' or 'manage-publications',
                       'edit_p': ln=='fr' and 'gerer-les-publications/editer' or 'manage-publications/edit',
                       'remove_p': ln=='fr' and 'gerer-les-publications/supprimer' or 'manage-publications/remove',
                       'export_p': ln=='fr' and 'gerer-les-publications/exporter' or 'manage-publications/export',
                       'manage_a_p': ln=='fr' and 'gerer-mon-compte' or 'manage-my-account',
                       'basket_p': ln=='fr' and 'gerer-mon-compte/collections' or 'manage-my-account/collections',
                       'people_p': ln=='fr' and 'gerer-les-publications/people' or 'manage-publications/people',
        } 

    def tmpl_navtrailbox_body(self, ln, title, previous_links, separator, prolog, epilog):
        """Create navigation trail box body
           Parameters:
          - 'ln' *string* - The language to display
          - 'title' *string* - page title;
          - 'previous_links' *string* - the trail content from site title until current page (both ends exclusive)
          - 'prolog' *string* - HTML code to prefix the navtrail item with
          - 'epilog' *string* - HTML code to suffix the navtrail item with
          - 'separator' *string* - HTML code that separates two navtrail items
           Output:
          - text containing the navtrail
        """
        _ = gettext_set_language(ln)
        previous_links = previous_links.strip()
        title = title.strip()
        
        if title == CFG_SITE_NAME:
            # Homepage
            return """
      <ul id="breadcrumbs">
        <li>%s</li>
        <li class="last">Infoscience</li>
      </ul>""" % create_html_link('http://www.epfl.ch', {}, 'EPFL', {'title': _("EPFL Homepage")})
        
        if previous_links and not previous_links.startswith('<li'):
            previous_links = '<li>%s</li>' % previous_links                    
                    
        if title and not title.startswith('<li'):
            title = '<li class="last">%s</li>' % saxutils.unescape(title)

        out = """
      <ul id="breadcrumbs">
        <li>%s</li>
        <li>%s</li>
        %s
        %s
      </ul>"""     
        return out % (create_html_link('http://www.epfl.ch', {}, 'EPFL', {'title': _("EPFL Homepage")}),
                      create_html_link('/', {'ln': ln}, 'Infoscience', {'title': _("Infoscience Homepage")}),
                      previous_links,
                      title)



    def detailed_record_container_top(self, recid, tabs, ln=CFG_SITE_LANG,
                                      show_similar_rec_p=True,
                                      creationdate=None,
                                      modificationdate=None, show_short_rec_p=True,
                                      citationnum=-1, referencenum=-1):
        """Prints the box displayed in detailed records pages, with tabs at the top.

        Returns content as it is if the number of tabs for this record
        is smaller than 2 => EPFL: no tabs!"""
        return ''

    def detailed_record_container_bottom(self, recid, tabs, ln=CFG_SITE_LANG,
                                         show_similar_rec_p=True,
                                         creationdate=None,
                                         modificationdate=None, show_short_rec_p=True):
        """Prints the box displayed in detailed records pages, with tabs at the top.

        Returns content as it is if the number of tabs for this record
        is smaller than 2 => EPFL: no tabs
  
        """
        # If no tabs, returns nothing
        return ''

    def detailed_record_mini_panel(self, recid, ln=CFG_SITE_LANG,
                                   format='hd',
                                   files='',
                                   reviews='',
                                   actions=''):
        """Displays the actions dock at the bottom of the detailed record
           pages. => EFL: no minipane"""
        return ''


epfl_header_html_fr = ""
epfl_header_html_en = ""
epfl_header_sig = ""

def epfl_header(ln):
    if ln == 'fr':
        global epfl_header_html_fr

        if not epfl_header_html_fr:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'header-no-local-search.fr.html'),
                      'r') as my_file:
                epfl_header_html_fr = my_file.read().replace('\n', '')

        return epfl_header_html_fr
    else:
        global epfl_header_html_en

        if not epfl_header_html_en:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'header-no-local-search.en.html'),
                      'r') as my_file:
                epfl_header_html_en = my_file.read().replace('\n', '')

        return epfl_header_html_en

def epfl_header_version():
    global epfl_header_sig

    if not epfl_header_sig:
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'header.sig.html'), 'r') as my_file:
            epfl_header_sig = my_file.read().replace('\n', '')

    return epfl_header_sig
