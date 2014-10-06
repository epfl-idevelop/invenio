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
        return ""
    
    patents = bfo.fields('013')
    
    template_output_patent_nr = '<li><span class="field-label">Patent :</span><ul class="record-metadata">%s</ul></li>'
    
    output = []
    # get number with data linked
    patents_nr = []
    patent_priority_dates = []
    
    # parse
    if patents:
        outer_list = "<ul>%s</u>"
        for patent in patents:
            if patent.has_key('a'):
                patent_output = ''
                
                # add country
                if patent.has_key('b'):
                    patent_output += patent['b']
                
                patent_output += patent['a'] 
                
                # add type of number
                if patent.has_key('c'):
                    patent_output += ' (' + patent['c'] + ')'
                    
                patents_nr.append(patent_output)
                
                # prority_dates are not shown, but are the same year as the publication date
                # if patent.has_key('d'):
                #    patent_priority_dates.append(patent['d'])
    
    # format
    if patents_nr:
        output_patent_nr = []
        for patent_nr in patents_nr:
            output_patent_nr.append("<li>%s</li>" % patent_nr)

        output.append(template_output_patent_nr % "".join(output_patent_nr))
        
    return outer_list % "".join(output)
    
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0