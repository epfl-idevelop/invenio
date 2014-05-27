# -*- coding: utf-8 -*-
"""
EPFL templates.
Websession handles admin menu and login links
"""
import urllib

from invenio.config import CFG_SITE_LANG, CFG_SITE_SECURE_URL, CFG_SITE_URL
from invenio.messages import gettext_set_language
from invenio import websession_templates

class Template(websession_templates.Template):
    """
    EPFL subclass of websession_template
    """
    
    def tmpl_account_adminactivities(self, ln, uid, guest, roles, activities):
        """
        Displays the admin activities block for this user
        Parameters:
          - 'ln' *string* - The language to display the interface in
          - 'uid' *string* - The used id
          - 'guest' *boolean* - If the user is guest
          - 'roles' *array* - The current user roles
          - 'activities' *array* - The user allowed activities
        """
        # load the right message language
        _ = gettext_set_language(ln)
        out = ""
        # guest condition
        if guest:
            return _("You seem to be a guest user. You have to %(x_url_open)slogin%(x_url_close)s first.") % \
                        {'x_url_open': '<a href="../youraccount/login?ln=' + ln + '">',
                         'x_url_close': '<a/>'}

        # no rights condition
        if not roles:
            return "<p>" + _("You are not authorized to access administrative functions.") + "</p>"

        # displaying form
        out += "<p>" + _("You are enabled to the following roles: %(x_role)s.") % {'x_role': ('<em>' + ", ".join(roles) + "</em>")} + '</p>'

        if activities:
            # print proposed links:
            activities.sort(lambda x, y: cmp(x.lower(), y.lower()))
            tmp_out = ''
            for action in activities:
                if action == "runbibedit":
                    tmp_out += """<br />&nbsp;&nbsp;&nbsp; <a href="%s/record/edit/">%s</a>""" % (CFG_SITE_URL, _("Run Record Editor"))
                if action == "runbibeditmulti":
                    tmp_out += """<br />&nbsp;&nbsp;&nbsp; <a href="%s/record/multiedit/">%s</a>""" % (CFG_SITE_URL, _("Run Multi-Record Editor"))
                if action == "runbibcirculation":
                    tmp_out += """<br />&nbsp;&nbsp;&nbsp; <a href="%s/admin/bibcirculation/bibcirculationadmin.py?ln=%s">%s</a>""" % (CFG_SITE_URL, ln, _("Run BibCirculation"))
                if action == "runbibmerge":
                    tmp_out += """<br />&nbsp;&nbsp;&nbsp; <a href="%s/record/merge/">%s</a>""" % (CFG_SITE_URL, _("Run Record Merger"))
                if action == "runbibswordclient":
                    tmp_out += """<br />&nbsp;&nbsp;&nbsp; <a href="%s/record/bibsword/">%s</a>""" % (CFG_SITE_URL, _("Run BibSword Client"))
                if action == "runbatchuploader":
                    tmp_out += """<br />&nbsp;&nbsp;&nbsp; <a href="%s/batchuploader/metadata?ln=%s">%s</a>""" % (CFG_SITE_URL, ln, _("Run Batch Uploader"))
                if action == "cfgbibformat":
                    tmp_out += """<br />&nbsp;&nbsp;&nbsp; <a href="%s/admin/bibformat/bibformatadmin.py?ln=%s">%s</a>""" % (CFG_SITE_URL, ln, _("Configure BibFormat"))
                    tmp_out += """<br />&nbsp;&nbsp;&nbsp; <a href="%s/kb?ln=%s">%s</a>""" % (CFG_SITE_URL, ln, _("Configure BibKnowledge"))
                if action == "cfgoaiharvest":
                    tmp_out += """<br />&nbsp;&nbsp;&nbsp; <a href="%s/admin/bibharvest/oaiharvestadmin.py?ln=%s">%s</a>""" % (CFG_SITE_URL, ln, _("Configure OAI Harvest"))
                if action == "cfgoairepository":
                    tmp_out += """<br />&nbsp;&nbsp;&nbsp; <a href="%s/admin/bibharvest/oairepositoryadmin.py?ln=%s">%s</a>""" % (CFG_SITE_URL, ln,  _("Configure OAI Repository"))
                if action == "cfgbibindex":
                    tmp_out += """<br />&nbsp;&nbsp;&nbsp; <a href="%s/admin/bibindex/bibindexadmin.py?ln=%s">%s</a>""" % (CFG_SITE_URL, ln, _("Configure BibIndex"))
                if action == "cfgbibrank":
                    tmp_out += """<br />&nbsp;&nbsp;&nbsp; <a href="%s/admin/bibrank/bibrankadmin.py?ln=%s">%s</a>""" % (CFG_SITE_URL, ln, _("Configure BibRank"))
                if action == "cfgwebaccess":
                    tmp_out += """<br />&nbsp;&nbsp;&nbsp; <a href="%s/admin/webaccess/webaccessadmin.py?ln=%s">%s</a>""" % (CFG_SITE_URL, ln, _("Configure WebAccess"))
                if action == "cfgwebcomment":
                    tmp_out += """<br />&nbsp;&nbsp;&nbsp; <a href="%s/admin/webcomment/webcommentadmin.py?ln=%s">%s</a>""" % (CFG_SITE_URL, ln, _("Configure WebComment"))
                if action == "cfgwebjournal":
                    tmp_out += """<br />&nbsp;&nbsp;&nbsp; <a href="%s/admin/webjournal/webjournaladmin.py?ln=%s">%s</a>""" % (CFG_SITE_URL, ln, _("Configure WebJournal"))
                if action == "cfgwebsearch":
                    tmp_out += """<br />&nbsp;&nbsp;&nbsp; <a href="%s/admin/websearch/websearchadmin.py?ln=%s">%s</a>""" % (CFG_SITE_URL, ln, _("Configure WebSearch"))
                if action == "cfgwebsubmit":
                    tmp_out += """<br />&nbsp;&nbsp;&nbsp; <a href="%s/admin/websubmit/websubmitadmin.py?ln=%s">%s</a>""" % (CFG_SITE_URL, ln, _("Configure WebSubmit"))
            if tmp_out:
                out += _("Here are some interesting web admin links for you:") + tmp_out

                out += "<br />" + _("For more admin-level activities, see the complete %(x_url_open)sAdmin Area%(x_url_close)s.") %\
                {'x_url_open': '<a href="' + CFG_SITE_URL + '/help/admin?ln=' + ln + '">',
                    'x_url_close': '</a>'}
        return out


    def tmpl_create_useractivities_menu(self, user_info, ln, selected, url_referer, guest, username, submitter, referee, admin, usebaskets, usemessages, usealerts, usegroups, useloans, usestats):
        """
        Returns the main navigation menu with actions based on user's
        priviledges

        @param ln:          The language to display the interface in
        @type ln:           string
        @param selected:    If the menu is currently selected
        @type selected:     boolean
        @param url_referer: URL of the page being displayed
        @type url_referer:  string
        @param guest:       If the user is guest
        @type guest:        string
        @param username:    The username (nickname or email)
        @type username:     string
        @param submitter:   If the user is submitter
        @type submitter:    boolean
        @param referee:     If the user is referee
        @type referee:      boolean
        @param admin:       If the user is admin
        @type admin:        boolean
        @param usebaskets:  If baskets are enabled for the user
        @type usebaskets:   boolean
        @param usemessages: If messages are enabled for the user
        @type usemessages:  boolean
        @param usealerts:   If alerts are enabled for the user
        @type usealerts:    boolean
        @param usegroups:   If groups are enabled for the user
        @type usegroups:    boolean
        @param useloans:    If loans are enabled for the user
        @type useloans:     boolean
        @param usestats:    If stats are enabled for the user
        @type usestats:     boolean
        @return: html menu of the user activities
        @rtype: string
        """
        # load the right message language
        _ = gettext_set_language(ln)
        out = ''
        if guest:
            return out
        out = """
            <ul class="menu hidden">
              <li><a href="%(secure_domain)s/curator/my_account/profile/?ln=%(ln)s">%(my_infoscience_label)s</a></li>              
              <li><a href="%(secure_domain)s/yourbaskets/display?category=P&amp;topic=default&amp;ln=%(ln)s">%(collections_label)s</a></li>
              <li><a href="%(secure_domain)s/youralerts/list?ln=%(ln)s">%(alerts_label)s</a></li>
            </ul>""" % {'secure_domain': CFG_SITE_SECURE_URL,
                        'ln': ln,
                        'sciper': user_info.get('external_uniqueidentifier', [None])[0] or user_info.get('external_cn', [None])[-1] or '',
                        'my_infoscience_label': _("My profile"),
                        'collections_label': _("My collections"),
                        'alerts_label': _("My alerts")
                       }
        junk = _("XX-Translate-test") 
        return out

    def tmpl_create_adminactivities_menu(self, ln, selected, url_referer, guest, username, submitter, referee, admin, usebaskets, usemessages, usealerts, usegroups, useloans, usestats, activities):
        """
        Returns the main navigation menu with actions based on user's
        priviledges

        @param ln:          The language to display the interface in
        @type ln:           string
        @param selected:    If the menu is currently selected
        @type selected:     boolean
        @param url_referer: URL of the page being displayed
        @type url_referer:  string
        @param guest:       If the user is guest
        @type guest:        string
        @param username:    The username (nickname or email)
        @type username:     string
        @param submitter:   If the user is submitter
        @type submitter:    boolean
        @param referee:     If the user is referee
        @type referee:      boolean
        @param admin:       If the user is admin
        @type admin:        boolean
        @param usebaskets:  If baskets are enabled for the user
        @type usebaskets:   boolean
        @param usemessages: If messages are enabled for the user
        @type usemessages:  boolean
        @param usealerts:   If alerts are enabled for the user
        @type usealerts:    boolean
        @param usegroups:   If groups are enabled for the user
        @type usegroups:    boolean
        @param useloans:    If loans are enabled for the user
        @type useloans:     boolean
        @param usestats:    If stats are enabled for the user
        @type usestats:     boolean
        @param activities: dictionary of admin activities
        @rtype activities: dict
        @return: html menu of the user activities
        @rtype: string
        """
        # load the right message language
        _ = gettext_set_language(ln)
        
        if not activities:
            return ''
        
        admin_action_list = {}
        
        tmpl = '              <li><a href="%s">%s</a></li>'
        admin_action_list['curator_functions'] = '\n'.join([
                     tmpl % ('/curator/dropbox', _("Dropbox")),
                     tmpl % ('/curator/delete', _("Delete by reference")),
                     tmpl % ('/curator/laboratories', _("Laboratories management")),
                     tmpl % ('/curator/stats/query', _("Laboratories stats")),
                     tmpl % ('/curator/authors', _("Authors management")),
                     tmpl % ('/curator/users/create', _("Create user")),
                     tmpl % ('/curator/metrics', _("Publication statistics / bibliometrics")),
                     #tmpl % ('/stats/', _("Site statistics")),
                     ])

        admin_action_list['getter_functions'] = '\n'.join([
                     tmpl % ('/curator/deduplicate/wos/list', _("Deduplicate")),
                     tmpl % ('/curator/getter/manual_match', _("Manual match")),
                     tmpl % ('/curator/getter/rejected_imports', _("Rejected imports")),
                     ])        
        
        activities = activities.items()
        activities.sort(lambda x, y: cmp(x[0], y[0]))
        admin_action_list['invenio_functions'] =  '\n'.join([tmpl % (url, label) for (label, url) in activities])
        out = """
            <ul class="menu hidden">
                <li><a href="/curator/admin">Curator</a>
                <ul>
                    %(curator_functions)s
                </ul>
                </li>
                <li><a href="#">Getter</a>
                <ul>
                    %(getter_functions)s
                </ul>
                </li>                
                <li><a href="">Invenio</a>
                <ul>
                    %(invenio_functions)s
                </ul>
                </li>                
            </ul>""" % (admin_action_list)


        return out


    def tmpl_navtrail(self, ln=CFG_SITE_LANG, title=""):
        """
        display the navtrail, e.g.:
        Your account > Your group > title
        @param title: the last part of the navtrail. Is not a link
        @param ln: language
        return html formatted navtrail
        """
        _ = gettext_set_language(ln)
        nav_h1 = '<a class="navtrail" href="%s/youraccount/display">%s</a>'
        nav_h2 = ""
        if (title != ""):
            nav_h2 = ' &gt; <a class="navtrail" href="%s/yourgroups/display">%s</a>'
            nav_h2 = nav_h2 % (CFG_SITE_URL, _("Your Groups"))

        return  nav_h1 % (CFG_SITE_URL, _("Your Account")) + nav_h2


    def tmpl_create_userinfobox(self, ln, url_referer, guest, username, submitter, referee, admin, usebaskets, usemessages, usealerts, usegroups, useloans, usestats):
        """
        Displays the user block
        Parameters:
          - 'ln' *string* - The language to display the interface in
          - 'url_referer' *string* - URL of the page being displayed
          - 'guest' *boolean* - If the user is guest
          - 'username' *string* - The username (nickname or email)
          - 'submitter' *boolean* - If the user is submitter
          - 'referee' *boolean* - If the user is referee
          - 'admin' *boolean* - If the user is admin
          - 'usebaskets' *boolean* - If baskets are enabled for the user
          - 'usemessages' *boolean* - If messages are enabled for the user
          - 'usealerts' *boolean* - If alerts are enabled for the user
          - 'usegroups' *boolean* - If groups are enabled for the user
          - 'useloans' *boolean* - If loans are enabled for the user
          - 'usestats' *boolean* - If stats are enabled for the user
        @note: with the update of CSS classes (cds.cds ->
            invenio.css), the variables useloans etc are not used in
            this function, since they are in the menus.  But we keep
            them in the function signature for backwards
            compatibility.
        """
        # load the right message language
        _ = gettext_set_language(ln)
        out = ''
        if guest:
            out += """<a href="%(sitesecureurl)s/youraccount/login?ln=%(ln)s%(referer)s">%(login)s</a>""" % {
                        'sitesecureurl': CFG_SITE_SECURE_URL,
                        'ln' : ln,
                        'referer' : url_referer and ('&amp;referer=%s' % urllib.quote(url_referer)) or '',
                        'login' : _('login')
                        }
        else:
            out += """<a class="userinfo" href="%(sitesecureurl)s/youraccount/logout?ln=%(ln)s">%(logout)s</a>""" % {
                    'sitesecureurl' : CFG_SITE_SECURE_URL,
                    'ln' : ln,
                    'logout' : _("logout"),
                }
            out += """ (<a href="%(sitesecureurl)s/youraccount/display?ln=%(ln)s">%(username)s</a>)""" % {
                    'sitesecureurl' : CFG_SITE_SECURE_URL,
                    'ln' : ln,
                    'username' : username
               }
        return out
