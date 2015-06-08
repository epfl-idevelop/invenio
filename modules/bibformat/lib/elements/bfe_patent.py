# -*- coding: utf-8 -*-
"""BibFormat element - Prints Patent Number"""

def format(bfo, short="no"):
    """
    Print Patent information.

    """
    # don't show anything at the moment on html brief
    # it may a good idea to put an information like "published or granted" like :
    # if b1:
    #  return "Granted/Published patent"
    # if a1:
    #  return "Pending patent"
    if short != "no":
        patents = bfo.fields('013')
        if patents:
            # TODO: order by date
            # return only the latest
            for patent in patents:
                if patent.has_key('a'):
                    return patent['a']
        return
    
    patents = bfo.fields('013')

    if bfo.lang != 'en':
        patent_text = 'Numéro de brevet'
        patents_text = 'Numéros de brevet'
    else:
        patent_text = 'Patent number'
        patents_text = 'Patent numbers'

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
        
    return outer_list % "".join(output)
    
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0