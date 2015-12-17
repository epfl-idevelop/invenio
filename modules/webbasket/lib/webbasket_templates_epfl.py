""" EPFL Templating for webbasket module """


import cgi

from invenio.messages import gettext_set_language
from invenio.webbasket_config import \
                       CFG_WEBBASKET_CATEGORIES, \
                       CFG_WEBBASKET_SHARE_LEVELS, \
                       CFG_WEBBASKET_DIRECTORY_BOX_NUMBER_OF_COLUMNS
from invenio.webmessage_mailutils import email_quoted_txt2html, \
                                         email_quote_txt, \
                                         escape_email_quoted_text
from invenio.htmlutils import get_html_text_editor
from invenio.config import \
     CFG_SITE_URL, \
     CFG_SITE_SECURE_URL, \
     CFG_SITE_LANG, \
     CFG_WEBBASKET_MAX_NUMBER_OF_DISPLAYED_BASKETS, \
     CFG_WEBBASKET_USE_RICH_TEXT_EDITOR
from invenio.webuser import get_user_info
from invenio.dateutils import convert_datetext_to_dategui

import invenio.webbasket_templates
from invenio.webbasket_templates import prettify_name, prettify_url

from invenio.webgroup_dblayer import get_group_infos

class Template(invenio.webbasket_templates.Template):
    """Templating class for webbasket module"""
    ######################## General interface ################################

    def tmpl_create_directory_box(self,
                                  category, topic,
                                  (grpid, group_name),
                                  bskid,
                                  (personal_info, personal_baskets_info),
                                  (group_info, group_baskets_info),
                                  public_info,
                                  ln):
        """
        EPFL
        Template for the directory-like menu.
        @param category: the selected category
        @param topic: the selected topic (optional)
        @param (grpid, groupname): the id and name of the selected group (optional)
        @param bskid: the id of the selected basket (optional)
        @param (personal_info, personal_baskets_info): personal baskets data
        @param (group_info, group_baskets_info): group baskets data
        @param public_info: public baskets data
        @param ln: language"""

        _ = gettext_set_language(ln)
        
        if not personal_info and not group_info and not public_info:
            return """
          <div class="box box-flat-panel home-navpanel local-color">
            <h3>%(no_baskets_label)s</h3>
            %(create_basket_label)s
          </div>""" % {'no_baskets_label': _('You have no personal or group collections'),
                       'create_basket_label': _('You may want to start by %(x_url_open)screating a new collection%(x_url_close)s.') % \
                             {'x_url_open': '<a href="/yourbaskets/create_basket?ln=%s">' % ln, 'x_url_close': '</a>'}}
        

        create_basket_link = """<a href="/yourbaskets/create_basket?topic=default&amp;ln=%(ln)s"><img src="/img/%(img)s" />%(label)s</a>""" % \
                                     {'ln': ln,
                                      'img': 'wb-create-basket.png',
                                      'label': _('Create collection')}
        
        if personal_info:
            personalbaskets_link = '<a href="/yourbaskets/display?category=%(category)s&amp;topic=default&amp;ln=%(ln)s">%(label)s</a>' % \
                                {'category': CFG_WEBBASKET_CATEGORIES['PRIVATE'], 'ln': ln,
                                 'label': _('Personal collections')}
            
            content_list = []
            if personal_baskets_info:
                for basket in personal_baskets_info:
                    basket_id = basket[0]
                    basket_name = basket[1]
                    nb_items = basket[4]
                    basket_link = """
                <li %(style)s><a href="/yourbaskets/display?category=%(category)s&amp;topic=default&amp;bskid=%(bskid)i&amp;ln=%(ln)s">%(basket_name)s <span class="nbdoccoll">(%(nb_items)i)</span></a></li>""" % \
                                 {'style': basket_id==bskid and 'class="current"' or "",
                                  'category': CFG_WEBBASKET_CATEGORIES['PRIVATE'],
                                  'bskid': basket_id,
                                  'ln': ln,
                                  'basket_name': cgi.escape(basket_name, True),
                                  'nb_items': nb_items}
                    content_list.append(basket_link)
            else:
                for basket in eval(personal_info[0][2] + ','):
                    basket_id = basket[0]
                    basket_name = basket[1]
                    basket_link = """
                <li %(style)s><a href="/yourbaskets/display?category=%(category)s&amp;topic=default&amp;bskid=%(bskid)i&amp;ln=%(ln)s">%(basket_name)s</a></li>""" % \
                                 {'style': basket_id==bskid and 'class="current"' or "",
                                  'category': CFG_WEBBASKET_CATEGORIES['PRIVATE'],
                                  'bskid': basket_id,
                                  'ln': ln,
                                  'basket_name': cgi.escape(basket_name, True)}
                    content_list.append(basket_link)

                
            personal_tab = """
            <li %(style)s>
              %(personalbaskets_link)s
              <ul>
%(baskets_list)s
              </ul>
            </li>""" % {'personalbaskets_link': personalbaskets_link,
                        'style': category == CFG_WEBBASKET_CATEGORIES['PRIVATE'] and not bskid and 'class="current open"' or 'class="open"',
                        'baskets_list': ''.join(content_list)}
        else:
            personal_tab = ''
            
        if group_info:
            groupbaskets_link = '<a href="/yourbaskets/display?category=%(category)s&amp;ln=%(ln)s">%(label)s</a>' % \
                                {'category': CFG_WEBBASKET_CATEGORIES['GROUP'], 'ln': ln,
                                 'label': _("Groups' collections")}
            
            content_list = []
            for group_and_baskets in group_info:
                group_id = group_and_baskets[0]
                try:
                    group_name = get_group_infos(group_id)[0][2]
                except IndexError:
                    group_name = group_and_baskets[1]
                nb_baskets = group_and_baskets[2]
                baskets = eval(group_and_baskets[3] + ',')
                basket_links_list = []
                for basket in baskets:
                    basket_id = basket[0]
                    basket_name = basket[1]
                    basket_link = """
                    <li %(style)s><a href="/yourbaskets/display?category=%(category)s&amp;group=%(group)i&amp;bskid=%(bskid)i&amp;ln=%(ln)s">%(basket_name)s</a></li>""" % \
                                 {'style': CFG_WEBBASKET_CATEGORIES['GROUP'] and basket_id==bskid and 'class="current"' or "",
                                  'category': CFG_WEBBASKET_CATEGORIES['GROUP'],
                                  'group': group_id,
                                  'bskid': basket_id,
                                  'ln': ln,
                                  'basket_name': cgi.escape(basket_name, True),}
                    basket_links_list.append(basket_link)
                
                grp_class = ''
                if group_id == grpid:
                    if bskid:
                        grp_class = 'inpath'
                    else:
                        grp_class = 'current open'
                
                group_link = """
                <li %(style)s><a href="/yourbaskets/display?category=%(category)s&amp;group=%(group)i&amp;ln=%(ln)s">%(group_name)s <span class="nbdoccoll">(%(nb_baskets)s)</span></a>
                  <ul>
%(baskets)s
                  </ul>
                </li>""" % {'style': grp_class and 'class="%s"' % grp_class or '',
                            'category': CFG_WEBBASKET_CATEGORIES['GROUP'],
                            'group': group_id,
                            'ln': ln,
                            'group_name': cgi.escape(group_name, True),
                            'nb_baskets': nb_baskets,
                            'baskets': ''.join(basket_links_list)}
                content_list.append(group_link)

            group_tab = """
            <li %(style)s>
              %(groupbaskets_link)s
              <ul>
%(groups_list)s
              </ul>
            </li>""" % {'groupbaskets_link': groupbaskets_link,
                        'style': category == CFG_WEBBASKET_CATEGORIES['GROUP'] and not grpid and 'class="current open"' or 'class="open"',
                        'groups_list': ''.join(content_list)}

        
        else:
            group_tab = ''
        
        return """
          <ul class="tree">
%s
%s
          </ul>""" % (personal_tab, group_tab)
        

    def tmpl_create_search_box(self,
                               category="",
                               topic="",
                               grpid=0,
                               topic_list=(),
                               group_list=(),
                               number_of_public_baskets=0,
                               p="",
                               n=0,
                               ln=CFG_SITE_LANG):
        """
        EPFL
        EXPERIMENTAL UI => rassurant... :-)"""
        _ = gettext_set_language(ln)
        
        action = """/yourbaskets/search"""
        
        select_options = create_search_box_select_options(category,
                                                          topic,
                                                          grpid,
                                                          topic_list,
                                                          group_list,
                                                          number_of_public_baskets,
                                                          ln)

        return """
    <form name="search_baskets" action="%(action)s" method="get" id="search-basket-form" class="search-form">
      <input type="hidden" name="n" value="" /><input type="hidden" name="ln" value="%(ln)s" />
      <input name="p" value="%(p)s" type="text" class="search"/><div class="search-filter">%(select_options)s</div><button type="submit" class="search-button" title="%(search_label)s">%(search_label)s</button>      
    </form>
    <div class="clear"></div>""" % {'action': action,
                   'search_label': _('Search'),
                   'p': p,
                   'select_options': select_options,
                   'ln': cgi.escape(ln, True)}

    def tmpl_search_results(self,
                            personal_search_results={},
                            total_no_personal_search_results=0,
                            group_search_results={},
                            total_no_group_search_results=0,
                            public_search_results={},
                            total_no_public_search_results=0,
                            all_public_search_results={},
                            total_no_all_public_search_results=0,
                            ln=CFG_SITE_LANG):
        """
        EPFL
        Template for the search results."""
        _ = gettext_set_language(ln)
        
        out = ''

        total_no_search_results = total_no_personal_search_results + total_no_group_search_results
        
        if not total_no_search_results:
            out += """
    <table class="table" style="margin-top: 20px;">
      <tr>
        <td>
        %(no_items_found_label)s
        </td>
      </tr>
    </table>""" % {'no_items_found_label': _('No items found.')}


        if total_no_personal_search_results:
            out += """
    <table class="table" style="margin-top: 20px;">
      <tr>
        <th style="padding-top: 10px;>
        <a name="%(personal_baskets_name)s"></a><strong>%(personal_baskets_label)s:</strong> %(items_found_label)s
        </th>
      </tr>""" % {'personal_baskets_label': _('Personal collections'),
                  'personal_baskets_name': "P",
                  'items_found_label': _('%i items found') % total_no_personal_search_results}

            for personal_search_result in personal_search_results.iteritems():
                basket_link = """<a href="/yourbaskets/display?category=%(category)s&amp;topic=%(topic)s&amp;bskid=%(bskid)i&amp;ln=%(ln)s" title="%(title_name)s">%(basket_name)s</a>""" % \
                              {'category': CFG_WEBBASKET_CATEGORIES['PRIVATE'],
                               'topic': cgi.escape(personal_search_result[1][1], True),
                               'bskid': personal_search_result[0],
                               'ln': ln,
                               'title_name': cgi.escape(personal_search_result[1][0], True),
                               'basket_name': cgi.escape(personal_search_result[1][0], True)}
                out += """
      <tr>
        <td>
        %(in_basket_label)s: %(items_found)s
        </td>
      </tr>""" % {'in_basket_label': _('In %(x_linked_basket_name)s') % \
                                     {'x_linked_basket_name': basket_link},
                  'items_found': _('%i items found') % personal_search_result[1][2]}
            out += """
    </table>"""


        if total_no_group_search_results:
            out += """
    <table class="table" style="margin-top: 20px;">
      <tr>
        <th>
        <a name="%(group_baskets_name)s"></a><strong>%(group_baskets_label)s:</strong> %(items_found_label)s
        </th>
      </tr>""" % {'group_baskets_label': _('Group collections'),
                  'group_baskets_name': "G",
                  'items_found_label': _('%i items found') % total_no_group_search_results}

            for group_search_result in group_search_results.iteritems():
                basket_link = """<a href="/yourbaskets/display?category=%(category)s&amp;group=%(group)i&amp;bskid=%(bskid)i&amp;ln=%(ln)s" title="%(title_name)s">%(basket_name)s</a>""" % \
                              {'category': CFG_WEBBASKET_CATEGORIES['GROUP'],
                               'group': group_search_result[1][1],
                               'bskid': group_search_result[0],
                               'ln': ln,
                               'title_name': cgi.escape(group_search_result[1][0], True),
                               'basket_name': cgi.escape(group_search_result[1][0], True)}
                out += """
      <tr>
        <td>
        %(in_basket_label)s: %(items_found)s
        </td>
      </tr>""" % {'in_basket_label': _('In %(x_linked_basket_name)s') % \
                                     {'x_linked_basket_name': basket_link},
                  'items_found': _('%i items found') % group_search_result[1][3]}
            out += """
    </table>"""

        return out

    def tmpl_display(self,
                     directory='',
                     content='',
                     search_box='',
                     search_results='',
                     ln=CFG_SITE_LANG):
        """
        EPFL
        Template for the generic display.
        @param directory: the directory-like menu (optional)
        @param content: content (of a basket) (optional)
        @param search_box: the search form (optional)
        @param search_results: the search results (optional)"""
        _ = gettext_set_language(ln)
        
        exports = ''
        if content:
            exports = """
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
          </div>""" % {'export_label': _('Export'), 
                       'export_web_label': _("Add to my website"),}

        
        out = """
        <div id="tools">
          <div class="button add">
              <a href="/yourbaskets/create_basket?ln=%(ln)s">
              <button class="icon"></button>
              <span class="label">%(create_label)s</span>
            </a>
          </div>
%(exports)s          
        </div>

        <div id="content" class="content">
%(content)s
%(search_title)s
%(search_box)s
%(search_results)s
        </div>
        <div class="right-col">     
          %(navigation)s
        </div>
        <div class="clear"></div>
        """
        if content:
            search_title = ''
        else:
            if search_results:
                search_title = '<h1 class="h2 no-bottom-margin">%s</h1>' % _("Search results")
            else:
                search_title = '<h1 class="h2 no-bottom-margin">%s</h1>' % _("Search collections for")
        return out % {'create_label': _("New personal collection"),
                      'ln': ln,
                      'exports': exports, 
                      'content': content, 
                      'search_title': search_title,
                      'search_box': search_box, 
                      'search_results': search_results,
                      'navigation': directory}
    
    
    def tmpl_create_basket(self, new_basket_name='',
                           new_topic_name='', create_in_topic=None, topics=[],
                           ln=CFG_SITE_LANG):
        """
        EPFL
        Template for basket creation
        @param new_basket_name: prefilled value (string)
        @param new_topic_name: prefilled value (string)
        @param topics: list of topics (list of strings)
        @param create_in_topic: preselected value for topic selection
        @param ln: language"""
        _ = gettext_set_language(ln)
        out = """
        <div id="tools">
          <div class="button add">
              <a href="/yourbaskets/create_basket?ln=%(ln)s">
              <button class="icon"></button>
              <span class="label">%(create_label)s</span>
            </a>
          </div>
        </div>
        <div id="content" class="content fullpage-content">
          <h1 class="h2">%(label)s</h1>
          <form name="create_basket" action="/yourbaskets/create_basket" method="post">
            <input type="hidden" name="new_topic_name" value="default"/>
            <label for="new_basket_name">%(name_label)s</label>
            <input type="text" id="new_basket_name" name="new_basket_name" value="%(basket_name)s"/>
            <button type="submit" value="%(label)s">%(label)s</button>
          </form>
        </div>""" % {'create_label': _("New personal collection"), 'ln': ln, 'label': _("Create new collection"), 'name_label': _("Collection name"), 'basket_name': new_basket_name, }
        return out


    ########################## functions on baskets #########################

    def tmpl_add(self,
                 recids=[],
                 category="",
                 bskid=0,
                 colid=0,
                 es_title="",
                 es_desc="",
                 es_url="",
                 note_body="",
                 personal_basket_list=(),
                 group_basket_list=(),
                 successful_add=False,
                 copy=False,
                 referer='',
                 ln=CFG_SITE_LANG):
        """
        EPFL
        Template for addding items to baskets."""
        _ = gettext_set_language(ln)
        out = """
        <div id="tools">
          <div class="button add">
              <a href="/yourbaskets/create_basket?ln=%(ln)s">
              <button class="icon"></button>
              <span class="label">%(create_label)s</span>
            </a>
          </div>

        </div>
        <div id="content" class="content fullpage-content">
          <h1 class="h2">%(label)s</h1>
%(content)s
        </div>""" 

        if successful_add:
            content = """
%(success_label)s.
<br /><br />
%(proceed_label)s""" % {'success_label': _('%i items have been successfully added to your collection') % (colid == -1 and 1 or len(recids)),
                        'proceed_label': _('Proceed to the %(x_url_open)scollection%(x_url_close)s') % \
                                         {'x_url_open': '<a href="/yourbaskets/display?category=%s&amp;bskid=%i&amp;ln=%s">' % (category, bskid, ln),
                                         'x_url_close': "</a>"}}
            if referer:
                if copy:
                    content +=  _(' or return to your %(x_url_open)sprevious collection%(x_url_close)s') % \
                            {'x_url_open': '<a href="%s">' % referer,
                             'x_url_close': '</a>'}
                else:
                    content +=  _(' or return to your %(x_url_open)ssearch%(x_url_close)s') % \
                            {'x_url_open': '<a href="%s">' % referer,
                             'x_url_close': '</a>'}
            else:
                referer='/'
                content += "."

            return out % {'label': _("Successfully added"), 'create_label': _("New personal collection"), 'ln': ln, 'content': content}
        
        select_options = create_add_box_select_options(category,
                                                       bskid,
                                                       personal_basket_list,
                                                       group_basket_list,
                                                       ln)

        hidden_recids = ""
        for recid in recids:
            hidden_recids += '<input type="hidden" name="recid" value="%s" />' % (recid,)

        action = "/yourbaskets/add"
        
        content = """
          <form name="add_to_basket" action="%(action)s" method="post">
            <p>%(create_new_basket)s</p>
            %(hidden_recids)s
            <input type="hidden" name="colid" value="%(colid)s" />
            <input type="hidden" name="copy" value="%(copy)i" />
            <input type="hidden" name="referer" value="%(referer)s" />
            <div class="navigation-bar" style="width: 652px;">
              <div class="group">
                <button type="submit" style="font-weight: bold" value="%(add_label)s">%(add_label)s</button>
                <button type="cancel" value="%(cancel_label)s" onClick="window.location='%(referer)s'">%(cancel_label)s</button>
              </div>
            </div>
          </form>""" % {'action': action,
               'create_new_basket': _("Please choose a collection: %(x_basket_selection_box)s (or %(x_url_open)screate a new one%(x_url_close)s first)") % \
                                    {'x_basket_selection_box': '&nbsp;<select name="b">%s</select>' % select_options,
                                     'x_url_open': '<a href="/yourbaskets/create_basket">',
                                     'x_url_close': '</a>'},
               'hidden_recids': hidden_recids,
               'colid': colid,
               'copy': copy and 1 or 0,
               'referer': referer,
               'add_label': _('Add items'),
               'cancel_label': _('Cancel')}

        return out % {'label': _("Adding %i items to your collections") % len(recids),
                      'content': content}

    def tmpl_confirm_delete(self, bskid,
                            (nb_users, nb_groups, nb_alerts),
                            category=CFG_WEBBASKET_CATEGORIES['PRIVATE'],
                            selected_topic="", selected_group_id=0,
                            ln=CFG_SITE_LANG):
        """
        EPFL
        display a confirm message
        @param bskid: basket id
        @param nb*: nb of users/groups/alerts linked to this basket
        @param category: private, group or external baskets are selected
        @param selected_topic: if private baskets, topic nb
        @param selected_group_id: if group: group to display baskets of
        @param ln: language
        @return: html output
        """
        _ = gettext_set_language(ln)
        title = _("Are you sure you want to delete this collection?")
        message = ''
        if nb_users:
            message += '<p>' + _("%i users are subscribed to this collection.")% nb_users + '</p>'
        if nb_groups:
            message += '<p>' + _("%i user groups are subscribed to this collection.")% nb_groups + '</p>'
        if nb_alerts:
            message += '<p>' + _("You have set %i alerts on this collection.")% nb_alerts + '</p>'
        out = """
        <div id="tools">
          <div class="button add">
              <a href="/yourbaskets/create_basket?ln=%(ln)s">
              <button class="icon"></button>
              <span class="label">%(create_label)s</span>
            </a>
          </div>    
        </div>
        <div id="content" class="content fullpage-content">
          <h1 class="h2">%(label)s</h1>
          %(message)s
          <div class="navigation-bar" style="width: 652px;">
            <div class="group">
              <form name="validate" action="%(url_ok)s" method="post" style="margin: 0; display: inline;">
                <input type="hidden" name="confirmed" value="1" />
                <input type="hidden" name="category" value="%(category)s" />
                <input type="hidden" name="group" value="%(group)i" />
                <input type="hidden" name="topic" value="%(topic)s" />
                <input type="hidden" name="ln" value="%(ln)s" />
                <input type="hidden" name="bskid" value="%(bskid)i" />
                <button type="submit" value="%(yes_label)s">%(yes_label)s</button>
              </form>
              <form name="cancel" action="%(url_cancel)s" method="get" style="margin: 0; display: inline;">
                <input type="hidden" name="category" value="%(category)s" />
                <input type="hidden" name="group" value="%(group)i" />
                <input type="hidden" name="topic" value="%(topic)s" />
                <input type="hidden" name="ln" value="%(ln)s" />
                <button type="submit" value="%(no_label)s">%(no_label)s</button>
              </form>
            </div>
          </div>  
        </div>""" % {'create_label': _("New personal collection"), 'ln': ln,
                     'label': title, 'message': message,
                     'bskid': bskid,
                     'url_ok': 'delete',
                     'url_cancel': 'display',
                     'category': category,
                     'topic': selected_topic,
                     'group': selected_group_id,
                     'ln':ln,
                     'yes_label': _("Yes"),
                     'no_label': _("Cancel")}
        
        return out

    def tmpl_edit(self, bskid, bsk_name, topic, topics, groups_rights, external_rights,
                  display_general=0, display_sharing=0, display_delete=0, ln=CFG_SITE_LANG):
        """
        EPFL
        Display interface for rights management over the given basket
        @param group_rights: list of (group id, name, rights) tuples
        @param external_rights: rights as defined in CFG_WEBBASKET_SHARE_LEVELS for public access.
        @param display_general: display fields name and topic, used with personal baskets
        @param display_sharing: display sharing possibilities
        @param display_delete: display delete basket button
        """
        _ = gettext_set_language(ln)
        general_box = ''
        if display_general:
            general_box = """
            <fieldset>
              <legend>%(legend)s</legend>
              <label for="bsk-newname">%(name_label)s</label>
              <input id="bsk-newname" type="text" name="new_name" value="%(basket_name)s"/>
              <input type="hidden" name="new_topic" value="default" />
            </fieldset>
            """ % {'legend': _("General settings"), 
                   'name_label': _("Collection name"),
                   'basket_name': cgi.escape(bsk_name, 1)}
        
        groups_body = ''
        if display_sharing:
            for (group_id, name, rights) in groups_rights:
                try:
                    name = get_group_infos(group_id)[0][2]
                except IndexError:
                    pass
                groups_body += """
              <label for="bsk-group-%(group_id)i">%(group_name)s:</label>
              %(menu)s<br />""" % {'group_id': group_id, 
                                   'group_name': name, 
                                   'menu': self.__create_group_rights_selection_menu(group_id, rights, ln)}
        
        groups_box = """
            <fieldset>
              <legend>%(legend)s</legend>
%(groups_body)s
              <button type="submit" name="add_group" value="%(add_label)s">%(add_label)s</button>
            </fieldset>
            """ % {'legend': _("Manage group rights"), 
                   'groups_body': groups_body,
                   'add_label': _("Add group")}

        delete_button = ''
        if display_delete:
            delete_button = '<button type="submit" name="delete" value="%(label)s" >%(label)s</button>' % {'label': _("Delete collection") }
        out = """
        <div id="tools">
          <div class="button add">
              <a href="/yourbaskets/create_basket?ln=%(ln)s">
              <button class="icon"></button>
              <span class="label">%(create_label)s</span>
            </a>
          </div>

        </div>
        <div id="content" class="content fullpage-content">
          <h1 class="h2">%(label)s</h1>
          <form name="edit" action="%(action)s" method="post">
            <input type="hidden" name="ln" value="%(ln)s" /><input type="hidden" name="bskid" value="%(bskid)i" /><input type="hidden" name="topic" value ="%(topic)s" />
%(general)s
%(groups)s
            <div class="navigation-bar" style="width: 652px;">
              <div class="group">
                <button type="submit" style="font-weight: bold" name="submit" value="%(submit_label)s">%(submit_label)s</button>
                <button type="submit" name="cancel" value="%(cancel_label)s" />%(cancel_label)s</button>
              </div>
              <div class="group" style="float: right; margin-right: 0;"> 
                %(delete_button)s  
              </div>
              <div class="clear"></div>
            </div>
          </form>
        </div>""" 
        return out % {'create_label': _("New personal collection"),
                      'label': _('Editing collection %(x_basket_name)s') % {'x_basket_name': cgi.escape(bsk_name)},
                      'action': '/yourbaskets/edit',
                      'ln': ln,
                      'topic': topic, 'bskid': bskid,
                      'general': general_box, 'groups': groups_box,
                      'submit_label': _("Save changes"), 'cancel_label': _("Cancel"),
                      'delete_button': delete_button}

    
    def __create_group_rights_selection_menu(self, group_id, current_rights, ln=CFG_SITE_LANG):
        """
        EPFL
        Private function. create a drop down menu for selection of rights
        @param current_rights: rights as defined in CFG_WEBBASKET_SHARE_LEVELS
        @param ln: language
        """
        _ = gettext_set_language(ln)
        elements = [(str(group_id) + '_' + 'NO', _("No rights")),
                    (str(group_id) + '_' + CFG_WEBBASKET_SHARE_LEVELS['READITM'],
                     _("View records")),
                    (str(group_id) + '_' + CFG_WEBBASKET_SHARE_LEVELS['ADDITM'],
                     '... ' + _("and") + ' ' + _("add records")),
                    (str(group_id) + '_' + CFG_WEBBASKET_SHARE_LEVELS['DELITM'],
                     '... ' + _("and") + ' ' + _("remove records")),
                    (str(group_id) + '_' + CFG_WEBBASKET_SHARE_LEVELS['MANAGE'],
                     '... ' + _("and") + ' ' + _("manage sharing rights"))
                    ]
        return self.__create_select_menu('groups', elements, str(group_id) + '_' + current_rights)

    def tmpl_add_group(self, bskid, selected_topic, groups=[], ln=CFG_SITE_LANG):
        """
        EPFL
        return form for selection of groups.
        @param bskid: basket id (int)
        @param selected_topic: topic currently displayed (int)
        @param groups: list of tuples (group id, group name)
        @param ln: language
        """
        _ = gettext_set_language(ln)
        
        if len(groups):
            updated = []
            for (group_id, group_name) in groups:
                try:
                    group_name = get_group_infos(group_id)[0][2]
                except IndexError:
                    pass
                updated.append((group_id, group_name))
            groups_menu = self.__create_select_menu('new_group', updated, selected_key=None)
        else:
            groups_menu = _("You are not a member of a group.")
        return """
        <div id="tools">
          <div class="button add">
              <a href="/yourbaskets/create_basket?ln=%(ln)s">
              <button class="icon"></button>
              <span class="label">%(create_label)s</span>
            </a>
          </div>        
        </div>
        <div id="content" class="content fullpage-content">
          <h1 class="h2">%(label)s</h1>
          <form name="edit" action="%(action)s" method="post">
            <input type="hidden" name="ln" value="%(ln)s" /><input type="hidden" name="bskid" value="%(bskid)i" /><input type="hidden" name="topic" value ="%(topic)s" />
            <fieldset>
              <legend>%(title)s</legend>
              %(menu)s
            </fieldset>
            
            <div class="navigation-bar" style="width: 652px;">
              <div class="group">
                <button type="submit" style="font-weight: bold" name="add_group" value="%(submit_label)s">%(submit_label)s</button>
                <button type="submit" name="group_cancel" value="%(cancel_label)s" />%(cancel_label)s</button>
              </div>
              <div class="clear"></div>
            </div>
          </form>
        </div>""" % {'label': _('Sharing collection to a new group'),
                     'create_label': _("New personal collection"),
                     'action': '/yourbaskets/edit',
                     'title': _("Add group"),
                     'menu': groups_menu, 
                     'cancel_label': _("Cancel"),
                     'submit_label': _("Add group"),
                     'ln': ln,
                     'topic': selected_topic,
                     'bskid': bskid,
                     }

 
    ############################ Baskets ###################################

    ##################################
    ########### BASKET VIEW ##########
    ##################################

    def tmpl_basket(self,
                    bskid,
                    name,
                    date_modification,
                    nb_items,
                    nb_subscribers,
                    (user_can_view_content,
                     user_can_edit_basket,
                     user_can_view_notes,
                     user_can_add_notes,
                     user_can_add_item,
                     user_can_delete_item),
                    nb_comments,
                    share_level,
                    selected_category=CFG_WEBBASKET_CATEGORIES['PRIVATE'],
                    selected_topic="",
                    selected_group=0,
                    items=[],
                    of='hb',
                    ln=CFG_SITE_LANG):
        """
        EPFL
        Template for basket display."""

        out = ""
        
        if not of.startswith('x'):
            out += self.tmpl_basket_header(bskid,
                                           name,
                                           nb_items,
                                           nb_subscribers,
                                           date_modification,
                                           (user_can_view_content,
                                            user_can_edit_basket,
                                            user_can_view_notes),
                                           selected_category,
                                           nb_comments,
                                           selected_topic,
                                           share_level,
                                           ln)

        if not of.startswith('x'):
            out += self.tmpl_basket_footer(bskid,
                                           nb_items,
                                           (user_can_view_content,
                                            user_can_edit_basket),
                                           selected_category,
                                           selected_topic,
                                           share_level,
                                           ln)

        out += self.tmpl_basket_content(bskid,
                                        (user_can_view_content,
                                         user_can_view_notes,
                                         user_can_add_notes,
                                         user_can_add_item,
                                         user_can_delete_item),
                                        selected_category,
                                        selected_topic,
                                        selected_group,
                                        items,
                                        of,
                                        ln)

        return out

    def tmpl_basket_header(self,
                           bskid,
                           name,
                           nb_items,
                           nb_subscribers,
                           date_modification,
                           (user_can_view_content,
                            user_can_edit_basket,
                            user_can_view_notes),
                           selected_category,
                           nb_comments,
                           selected_topic,
                           share_level,
                           ln=CFG_SITE_LANG):
        """
        EPFL
        Template for basket header display."""

        _ = gettext_set_language(ln)
        edit_button = ''
        delete_button = ''
        if user_can_edit_basket:
            edit_button = '<a href="/yourbaskets/edit?bskid=%i&amp;topic=default&amp;ln=%s" class="button">%s</a>' % (bskid, ln, _("Edit collection"))
            delete_button = '<a href="/yourbaskets/edit?bskid=%i&amp;topic=default&amp;delete=1&amp;ln=%s" class="button">%s</a>' % (bskid, ln, _("Delete collection"))
        
        out = """
          <h1 class="h2">%(title)s</h1>
          <div class="navigation-bar" style="width: 652px;">
            <div class="group"><span>%(status_label)s</span></div>
            <div class="group" style="float: right; margin-right: 0;"> 
              %(edit_button)s
              %(delete_button)s  
            </div>
            <div class="clear"></div>
          </div>
        """ 
        return out % {'title': cgi.escape(name, True),
                      'status_label': _("%(nb)i records, last modified on %(date)s") % {'nb': nb_items, 'date': date_modification},
                      'edit_button': edit_button,
                      'delete_button': delete_button,}       
        
        
    def tmpl_basket_footer(self,
                           bskid,
                           nb_items,
                           (user_can_view_content,
                            user_can_edit_basket),
                           selected_category,
                           selected_topic,
                           share_level=None,
                           ln=CFG_SITE_LANG):
        """
        EPFL
        Template for basket footer display."""
        return ''

    def tmpl_basket_content(self,
                            bskid,
                            (user_can_view_content,
                             user_can_view_notes,
                             user_can_add_notes,
                             user_can_add_item,
                             user_can_delete_item),
                            selected_category=CFG_WEBBASKET_CATEGORIES['PRIVATE'],
                            selected_topic="",
                            selected_group=0,
                            items=[],
                            of='hb',
                            ln=CFG_SITE_LANG):
        """
        EPFL
        Template for basket content display."""

        if not of.startswith('x'):
            _ = gettext_set_language(ln)
            items_html = """
        <table class="table infoscience_export no-margin">
          <tbody>"""
            if user_can_view_content:
                if not(items):
                    items_html += """
            <tr>
              <td style="text-align:center; height:100px">%s</td>
            </tr>""" % _("collection is empty")
                else:
                    count = 0
                    for item in items:
                        count += 1
                        copy = 1
                        go_up = go_down = delete = 0
                        if user_can_add_item:
                            go_up = go_down = 1
                            if item == items[0]:
                                go_up = 0
                            if item == items[-1]:
                                go_down = 0
                        if user_can_delete_item:
                            delete = 1
                        items_html += self.__tmpl_basket_item(count=count,
                                                              bskid=bskid,
                                                              item=item,
                                                              uparrow=go_up,
                                                              downarrow=go_down,
                                                              copy_item=copy,
                                                              delete_item=delete,
                                                              view_notes=False,
                                                              add_notes=False,
                                                              selected_category=selected_category,
                                                              selected_topic=selected_topic,
                                                              selected_group=selected_group,
                                                              ln=ln)
            else:
                items_html += """
            <tr>
              <td style="text-align:center; height:100px">%s</td>
            </tr>""" % _("You do not have sufficient rights to view this basket's content.")
            items_html += """
          </tbody>
        </table>
        <form id="infoscience-searchform" action="/curator/convert/marcxml">
          <input type="hidden" name="bskid" value="%s" />
        </form>""" % bskid
            return items_html
        else:
            items_xml = ""
            for item in items:
                items_xml += item[4] + "\n"
            return items_xml


    def __tmpl_basket_item(self,
                           count,
                           bskid,
                           item,
                           uparrow=0,
                           downarrow=0,
                           copy_item=0,
                           delete_item=0,
                           view_notes=0,
                           add_notes=0,
                           selected_category=CFG_WEBBASKET_CATEGORIES['PRIVATE'],
                           selected_topic="",
                           selected_group=0,
                           ln=CFG_SITE_LANG):
        """
        EPFL
        Template for basket item display within the basket content."""

        _ = gettext_set_language(ln)

        (recid, colid, nb_cmt, last_cmt, val, dummy) = item

        if uparrow:
            moveup_url = "/yourbaskets/modify?action=moveup&amp;bskid=%(bskid)i&amp;recid=%(recid)i"\
                         "&amp;category=%(category)s&amp;topic=%(topic)s&amp;group_id=%(group)i&amp;ln=%(ln)s" % \
                         {'bskid': bskid,
                          'recid': recid,
                          'category': selected_category,
                          'topic': selected_topic,
                          'group': selected_group,
                          'ln': ln}
            moveup = """<a href="%s" class="move-up"></a>""" % moveup_url
        else:
            moveup = '<div class="move-up"></div>'

        if downarrow:
            movedown_url = "/yourbaskets/modify?action=movedown&amp;bskid=%(bskid)i&amp;recid=%(recid)i"\
                         "&amp;category=%(category)s&amp;topic=%(topic)s&amp;group_id=%(group)i&amp;ln=%(ln)s" % \
                         {'bskid': bskid,
                          'recid': recid,
                          'category': selected_category,
                          'topic': selected_topic,
                          'group': selected_group,
                          'ln': ln}
            movedown = """<a href="%s" class="move-down"></a>""" % movedown_url
        else:
            movedown = ""

        if copy_item:
            copy_url = "/yourbaskets/modify?action=copy&amp;bskid=%(bskid)i&amp;recid=%(recid)i"\
                       "&amp;category=%(category)s&amp;topic=%(topic)s&amp;group_id=%(group)i&amp;ln=%(ln)s" % \
                       {'bskid': bskid,
                        'recid': recid,
                        'category': selected_category,
                        'topic': selected_topic,
                        'group': selected_group,
                        'ln': ln}
            copy_img = "/img/wb-copy-item.png"
            copy = """<a href="%s"><img src="%s" alt="%s" />%s</a>""" % \
                       (copy_url, copy_img, _("Copy item"), _("Copy item"))
            copy = '<div class="button copy"><a href="%s"><button class="icon"></button><span class="label">%s</span></a></div>' % (copy_url, _("Copy item"))
        else:
            copy = ""

        if delete_item:
            remove_url = "/yourbaskets/modify?action=delete&amp;bskid=%(bskid)i&amp;recid=%(recid)i"\
                         "&amp;category=%(category)s&amp;topic=%(topic)s&amp;group=%(group)i&amp;ln=%(ln)s" % \
                         {'bskid': bskid,
                          'recid': recid,
                          'category': selected_category,
                          'topic': selected_topic,
                          'group': selected_group,
                          'ln': ln}
            remove = '<div class="button cross"><a href="%s"><button class="icon"></button><span class="label">%s</span></a></div>' % (remove_url, _("Remove item"))
        else:
            remove = ""

        out = """
            <tr>
              <td class="bskcontentoptions">%(moveup)s%(movedown)s</td>
              <td class="bskcontent">%(content)s
                 <p class="infoscience_links"><a href="/record/%(recid)s">%(detailed_record_label)s</a></p>
              </td>
              <td class="bskbasketheaderoptions">
                %(copy)s
                %(remove)s
              </td>
            </tr>"""
        out = out % {'moveup': moveup,
                     'movedown': movedown,
                     'content': colid >= 0 and val or self.tmpl_create_pseudo_item(val),
                     'bskid': bskid,
                     'recid': recid,
                     'detailed_record_label': _("Detailed record"),
                     'category': selected_category,
                     'topic': selected_topic,
                     'group': selected_group,
                     'copy': copy,
                     'remove': remove,
                     'ln': ln}
        return out

    #############################################
    ########## BASKET SINGLE ITEM VIEW ##########
    #############################################

    def tmpl_basket_single_item(self,
                                bskid,
                                name,
                                nb_items,
                                (user_can_view_content,
                                 user_can_view_notes,
                                 user_can_add_notes,
                                 user_can_delete_notes),
                                selected_category=CFG_WEBBASKET_CATEGORIES['PRIVATE'],
                                selected_topic="",
                                selected_group=0,
                                item=(),
                                comments=(),
                                previous_item_recid=0,
                                next_item_recid=0,
                                item_index=0,
                                optional_params={},
                                of='hb',
                                ln=CFG_SITE_LANG):
        
        """
        EPFL
        Template for basket's single item display."""

        out = ""

        if of != 'xm':
            out += self.tmpl_basket_single_item_header(bskid,
                                                       name,
                                                       nb_items,
                                                       selected_category,
                                                       selected_topic,
                                                       selected_group,
                                                       previous_item_recid,
                                                       next_item_recid,
                                                       item_index,
                                                       ln)

        if of != 'xm':
            out += self.tmpl_basket_single_item_footer(bskid,
                                                       selected_category,
                                                       selected_topic,
                                                       selected_group,
                                                       previous_item_recid,
                                                       next_item_recid,
                                                       ln)

        out += self.tmpl_basket_single_item_content(bskid,
                                                    (user_can_view_content,
                                                     user_can_view_notes,
                                                     user_can_add_notes,
                                                     user_can_delete_notes),
                                                    selected_category,
                                                    selected_topic,
                                                    selected_group,
                                                    item,
                                                    comments,
                                                    item_index,
                                                    optional_params,
                                                    of,
                                                    ln)

        return out


def create_search_box_select_options(category,
                                     topic,
                                     grpid,
                                     topic_list,
                                     group_list,
                                     number_of_public_baskets,
                                     ln):
    """
    EPFL
    Returns an html list of options for the select form field of the search box."""
    _ = gettext_set_language(ln)
    
    FIELDNAME = 'b'
    
    if category:
        if topic:
            b = CFG_WEBBASKET_CATEGORIES['PRIVATE']
        elif grpid:
            b = CFG_WEBBASKET_CATEGORIES['GROUP'] + '_' + str(grpid)
        else:
            b = category
    else:
        b = ""

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
    
    
    selected_field = ''
    options = []
    value = ''
    if b == value:
        selected_field = _("All my collections")
    options.append(tmpl % {'fieldname': FIELDNAME, 
                           'value': value,
                           'checked': b==value and 'checked="checked"' or '',
                           'checked_class': b==value and 'class="current"' or '',
                           'label': _("All my collections")})
    if topic_list:
        value = CFG_WEBBASKET_CATEGORIES['PRIVATE']
        if b == value:
            selected_field = _("My personal collections")
        options.append(tmpl % {'fieldname': FIELDNAME, 
                               'value': value,
                               'checked': b==value and 'checked="checked"' or '',
                               'checked_class': b==value and 'class="current"' or '',
                               'label': _("My personal collections")})
        
    if group_list:
        value = CFG_WEBBASKET_CATEGORIES['GROUP']
        if b == value:
            selected_field = _("My groups' collections")
        options.append(tmpl % {'fieldname': FIELDNAME, 
                               'value': value,
                               'checked': b==value and 'checked="checked"' or '',
                               'checked_class': b==value and 'class="current"' or '',
                               'label': _("My groups' collections")})
        
        for (group_id, group_name) in group_list:
            value = "G_%i" % group_id
            try:
                group_name = get_group_infos(group_id)[0][2]
            except IndexError:
                pass
            if b == value:
                selected_field = group_name
            options.append(tmpl % {'fieldname': FIELDNAME, 
                                   'value': value,
                                   'checked': b==value and 'class="subfilter" checked="checked"' or 'class="subfilter"',
                                   'checked_class': b==value and 'class="current"' or '',
                                   'label': group_name})
    
    return out % (selected_field, ''.join(options))


def create_add_box_select_options(category,
                                  bskid,
                                  personal_basket_list,
                                  group_basket_list,
                                  ln):
    """
    EPFL
    Returns an html list of options for the select form field of the add box."""
    _ = gettext_set_language(ln)
    out = ""
    options = []

    if category and bskid:
        if category == CFG_WEBBASKET_CATEGORIES['PRIVATE']:
            b = CFG_WEBBASKET_CATEGORIES['PRIVATE'] + '_' + str(bskid)
        elif category == CFG_WEBBASKET_CATEGORIES['GROUP']:
            b = CFG_WEBBASKET_CATEGORIES['GROUP'] + '_' + str(bskid)
        elif category == CFG_WEBBASKET_CATEGORIES['EXTERNAL']:
            b = CFG_WEBBASKET_CATEGORIES['EXTERNAL'] + '_' + str(bskid)
        else:
            b = ""
    else:
        b = ""

    #option list format: [ name, value, 1st level: True/False, 2nd level: True/False]
    #   name: the name of the option, it will be used as its label in the list.
    #   value: the value of the option that will be sent as a POST variable through
    #          the select form field
    #   1st level: bold, no margin, used for categories
    #   2nd level: bold, small margin, used for topics and groups
    #   * when both levels are False: normal font, big margin,
    #     used for actual options *

    # Let's set the default "Choose a basket..." option first.
    #options= [(_("Choose a basket..."), str(-1), False, False)]
    out += """
            <option style="%(style)s" value="%(value)i">%(label)s</option>""" % \
                          {'style': "font-weight: normal;",
                           'value': -1,
                           'label': _("*** collection name ***")}

    # Then, we parse the personal and group basket lists and dynamically create
    # the list of options
    if personal_basket_list:
        options.append((_("My personal collections"), None, True, False))
        for personal_topic in personal_basket_list:
            personal_topic_name = cgi.escape(personal_topic[0], True)
            personal_baskets = eval(personal_topic[1] + ",")
            for personal_basket in personal_baskets:
                personal_basket_name = cgi.escape(personal_basket[1], True)
                personal_basket_value = CFG_WEBBASKET_CATEGORIES['PRIVATE'] + "_" + str(personal_basket[0])
                options.append((personal_basket_name, personal_basket_value, False, False))

    if group_basket_list:
        options.append((_("My groups' collections"), None, True, False))
        for group_group in group_basket_list:
            group_group_name = cgi.escape(group_group[1], True)
            try:
                group_group_name = get_group_infos(group_group[0])[0][2]
            except IndexError:
                pass
            group_baskets = eval(group_group[2] + ",")
            options.append((group_group_name, None, False, True))
            for group_basket in group_baskets:
                group_basket_name = cgi.escape(group_basket[1], True)
                group_basket_value = CFG_WEBBASKET_CATEGORIES['GROUP'] + "_" + str(group_basket[0])
                options.append((group_basket_name, group_basket_value, False, False))

    if len(options) == 3:
        # In case we only have 1 option, pretend b has the value of that option
        # so that it is selected by default.
        b = options[2][1]

    for option in options:
        out += """
            <option style="%(style)s"%(value)s%(selected)s%(disabled)s>%(label)s</option>""" % \
                          {'value': not ( option[2] or option[3] ) and ' value="' + option[1] + '"' or '',
                           'label': option[0],
                           'selected': option[1] == b and ' selected="selected"' or '',
                           'disabled': ( option[2] or option[3] ) and ' disabled="disabled"' or '',
                           'style': option[2] and "font-weight: bold;" or \
                           option[3] and "font-weight: bold; margin-left: 5px;" or \
                           "font-weight: normal; margin-left: 10px;"}

    return out
