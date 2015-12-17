"""
BibFormat element - Prints links to detailed record, similar records and fulltext
"""

from invenio.messages import gettext_set_language
from invenio.bibformat_elements.bfe_epfl_fulltext import get_files

from invenio.access_control_engine import acc_authorize_action

def can_edit(bfo):
    user_info = bfo.user_info
    
    at_epfl = bfo.field("973__a") == 'EPFL'
    thesis = bfo.field('980__a') == 'THESIS'
        
    # EPFL Theses cannot be edited via websubmit interface.    
    if at_epfl and thesis:
        (auth_code, auth_message) = acc_authorize_action(user_info, 'submit_thesis')
        if auth_code == 0:
            return True
        return False
    
    sciper = user_info.get('external_uniqueidentifier', [None])[0]
    labs = bfo.fields("909C0p")
    # member of labs ?
    for lab in labs:
        (auth_code, auth_message) = acc_authorize_action(user_info, 'submit_epfl', categ=lab)
        if auth_code == 0:
            return True
        
    # author of publication ?
    if sciper:
        scipers = bfo.fields('700__g')
        if sciper in scipers:
            return True
        # original submitter ?
        scipers = bfo.fields('917Z8x')
        if sciper in scipers:
            return True
        
    # admin ?
    (auth_code, auth_message) = acc_authorize_action(user_info, 'submit_epfl')
    if auth_code == 0:
        return True

    return False


def format_element(bfo):
    """
    This is the format for formatting fulltext links in the mini panel.
    """
    _ = gettext_set_language(bfo.lang)
            
    links = [('/record/%s?ln=%s' % (bfo.recID, bfo.lang), _("Detailed record"))]
    template = '<a href="%s">%s</a>'
    
    if bfo.field("980__c") == 'HIDDEN':
        return ''.join([template % link for link in links])
    
    (main_documents, additional_documents, external_documents) = get_files(bfo)
    if main_documents:
        if len(main_documents) + len(additional_documents) == 1:
            links.append((main_documents[0][0], _("Fulltext")))
        else:
            links.append(('/record/%s/files?ln=%s' % (bfo.recID, bfo.lang), _("Fulltext")))
    
    return ''.join([template % link for link in links])


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
