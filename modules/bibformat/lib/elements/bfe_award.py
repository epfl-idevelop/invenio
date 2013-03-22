# -*- coding: utf-8 -*-
"""BibFormat element - Prints Award information"""


from invenio.bibknowledge import get_kb_mapping

def format(bfo):
    """
    Print Award.

    """
    output = ''
    award_field = bfo.field('586__a')
    if award_field and award_field.strip():
        if not ',' in award_field:
            award_name = award_field.strip()
            award_name = get_kb_mapping(kb_name='awards', key=award_name, default=award_name)
            if type(award_name) == dict:
                award_name = award_name['value']
            return award_name

        award_name = ','.join(award_field.split(',')[:-1])
        award_year = award_field.split(',')[-1].strip()
        award_name = get_kb_mapping(kb_name='awards', key=award_name, default=award_name)
        if type(award_name) == dict:
            award_name = award_name['value']
        output = '%s, %s' % (award_name, award_year)
               
    return output