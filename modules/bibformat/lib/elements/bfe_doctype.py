# -*- coding: utf-8 -*-
"""BibFormat element - Prints collection identifier"""

from invenio.messages import gettext_set_language

def format(bfo):
    """
    Prints the collection identifier.
    Translate using given knowledge base.    
    """
    _ = gettext_set_language(bfo.lang)
    collection = bfo.field("980__a")

    if collection == 'ARTICLE':
        out = _("Journal article")
    elif collection == 'BOOK':
        out = _("Book")
    elif collection == 'CHAPTER':
        out = _("Book Chapter")
    elif collection == 'CONF':
        out = _("Conference paper")
    elif collection == 'LECTURE':
        out = _("Lecture")
    elif collection == 'REPORT':
        out = _("Report")
    elif collection == 'REVIEW':
        out = _("Review")
    elif collection =='PATENT':
        out = _("Patent")
    elif collection == 'PERSON':
        out = _("Researcher's profile")
    elif collection == 'POLY':
        out = _("Teaching document")
    elif collection == 'POSTER':
        out = _("Poster")
    elif collection == 'PROC':
        out = _("Conference proceedings")
    elif collection == 'STANDARD':
        out = _("Standard")
    elif collection == 'STUDENT':
        out = _("Student project")
    elif collection == 'TALK':
        out = _("Presentation / Talk")
    elif collection == 'THESIS':
        out = _("Thesis")
    elif collection == 'WORKING':
        out = _("Working paper")
    else:
        out = _("Record")
    return out
