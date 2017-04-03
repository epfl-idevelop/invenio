# -*- coding: utf-8 -*-
"""BibFormat element - Prints Patent Number"""

def format(bfo, short="no", add_link_to_epo=False):
    """
    Print Patent information.

    """
    # it may a good idea to put an information like "published or granted" like :
    # if b1:
    #  return "Granted/Published patent"
    # if a1:
    #  return "Pending patent"
    if short != "no":
        patent_to_print = ""
        patents = bfo.fields('013', escape=2)
        if patents:
            # return only the latest
            for patent in patents:
                if patent.has_key('a'):
                    patent_to_print = patent['a']
                    return patent_to_print
        return

    url_to_espacenet = "http://worldwide.espacenet.com/searchResults?compact=false&PN=%s&ST=advanced&locale=en_EP&DB=EPODOC"
    patents = bfo.fields('013', escape=2)

    tto_file_number = ""

    for external_id in bfo.fields('035__a'):
        if external_id and external_id.find('(TTO)') != -1:
            tto_file_number = "%s" % external_id.replace(' (TTO)', '')

    if bfo.lang != 'en':
        patent_text = 'Numéro de brevet'
        patents_text = 'Numéros de brevet'
        dossier_number_text = 'Numéro de dossier TTO'
    else:
        patent_text = 'Patent number'
        patents_text = 'Patent numbers'
        dossier_number_text = 'TTO Reference number'

    template_output_patent_nr = '<li style="list-style-image:none;"><span class="field-label">%s: <ul style="font-weight:normal;margin-left:10px;">%s</ul></span></li>'
    
    output = []
    # get number with data linked
    patents_nr = []
    patent_priority_dates = []
    outer_list = '<ul class="record-metadata">%s</u>'

    # parse
    if patents:
        for patent in patents:
            if patent.has_key('a'):
                patent_output = patent['a']
                
                # add type of number
                if patent.has_key('c'):
                    patent_output += ' (' + patent['c'] + ')'

                if add_link_to_epo:
                    url_fullfiled = url_to_espacenet % patent['a']
                    patent_output = '<a href="%s" target="_blank">%s</a>' % (url_fullfiled, patent_output)

                patents_nr.append(patent_output)
                
                # priority_dates are not shown, but are the same year as the publication date
                # if patent.has_key('d'):
                #    patent_priority_dates.append(patent['d'])
    
    # format
    if patents_nr:
        output_patent_nr = []
        for patent_nr in patents_nr:
            output_patent_nr.append("<li>%s</li>" % patent_nr)

        if len(output_patent_nr) > 1:
            patent_title = patents_text
        else:
            patent_title = patent_text

        output.append(template_output_patent_nr % (patent_title, "".join(output_patent_nr)))

    output_to_return = outer_list % "".join(output)

    if tto_file_number:
        output_to_return += outer_list % '<li><span class="field-label">' \
                            + dossier_number_text + ':</span>&nbsp;' +\
                            tto_file_number + '</li>'

    return output_to_return
    
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0