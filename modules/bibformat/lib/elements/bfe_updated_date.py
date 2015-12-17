"""BibFormat element - Prints the modified date
"""
from invenio.search_engine import get_modification_date, get_creation_date
from invenio.messages import gettext_set_language


def format_element(bfo, format='%Y-%m-%d', date_format='%Y-%m-%d'):
    '''
    Get the record modification date.
    <b>Note:</b> parameter <code>format</code> is deprecated

    @param date_format: The date format in MySQL syntax
    '''
    _ = gettext_set_language(bfo.lang)    
    recID = bfo.recID

    return _("Record created on %(creation_date)s, modified on %(modification_date)s") % {
            'creation_date': get_creation_date(recID, "%Y-%m-%d"),
            'modification_date': get_modification_date(recID, "%Y-%m-%d")}

