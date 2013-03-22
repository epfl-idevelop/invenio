from invenio.messages import gettext_set_language
from invenio.access_control_engine import acc_authorize_action
from invenio import webuser
from invenio.webuser import isGuestUser

from invenio.bibformat_elements.bfe_brief_links import can_edit

def get_pending_informations(bfo):
    """
    Parse value from Curator to get pending status,
    trough jQuery in an AJAX way
    """
    query_url = "/curator/api/submission/recid/%s/pending_labs/" % bfo.recID
    
    script_wrapper = """<script type="text/javascript">%s</script>"""
            
    script = """
        $(document).ready(function()
        {
            $.getJSON('%s', function(data) {
                to_append = $('#record-container-%s');
 
                var starting_div = '<div id="record_pending_status">';
                var closing_div = '</div>';
                
                if (data['validate'].length > 0)
                {
                    var validate_text = '';
                    validate_text += 'Pending validation for<br />';
                    
                    $.each(data['validate'], function(index, url) {
                        validate_text += url + '<br />';
                    });
                    
                    to_append.append(starting_div + validate_text + closing_div);
                }

                if (data['import'].length > 0)
                {
                    var import_text = '';
                    import_text += 'Pending import for<br />';
                    
                    $.each(data['import'], function(index, url) {
                       import_text += url + '<br />';
                    });
                    
                    to_append.append(starting_div + import_text + closing_div);
                }
            });
        });
            """ % (query_url, bfo.recID)            
            
    return script_wrapper % script

def get_ask_for_removal_form(bfo):
    _ = gettext_set_language(bfo.lang)
    
    text_content = {'query_url': "/curator/delete/ask_for_removal/",
                    'field_required': _("This field is required"),
                    'wait_while_sending': _("Please wait while your message is being sent"),
                    'successful_sent': _("Your request has been successfully sent.")
                    }
    
    script = """
        <script type="text/javascript">
            $(document).ready(function()
            {
                trigger = $("#overlay_for_removal_trigger").overlay({
                                                   top:"center",
                                                   mask: {
                                                        color: '#000000',
                                                        loadSpeed: 200,
                                                        opacity: 0.6
                                                   },
                                                   closeOnClick: false,
                                                   api: true
                                                   });
                                                   
                $('#remove_reason_form').submit(function(event){
                    event.preventDefault();
                    if( !$('#remove_reason').val() ) 
                    {
                          $('#remove_reason').css('border', '2px groove red');
                          $('#remove_reason').after('<br /><span style="color: #AE0010;">%(field_required)s.</span>');
                    }
                    else
                    {
                        var datas = $('#remove_reason_form').serialize();
                        $('#modal-content-div').html('<p>%(wait_while_sending)s.</p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="/media/img/loadingAnimation.gif">');
                                            
                        $.post("%(query_url)s", datas,
                              function( data ) {
                                    $('#modal-content-div').html('<p>%(successful_sent)s</p><div class="navigation-bar" id="dialog_actions"><div class="group right"><button onclick="trigger.close();" type="button">Close</button></div></div>');
                              }
                        );
                    }
            });                        
                        
            });
        </script>
        """ % text_content

    link = '''<a href="#" id="overlay_for_removal_trigger" rel="#ask_for_removal_overlay">%s</a>''' % ( _("Ask for removal"))
    
    content_string = {'title': _("Removal request"),
                      'explanation': _("Please tell us the reason you want to remove it"),
                      'recid': bfo.recID,
                      'submit_button': _("Send request"),
                      'cancel_button': _("Cancel")
                      }
    
    overlay = '''<div class="modal" id="ask_for_removal_overlay">
                    <h3>%(title)s</h3>
                    <div id="modal-content-div" class="modal-content">
                            <p>%(explanation)s.</p>
                            
                            <form method="post" id="remove_reason_form">
                                <label for="remove_reason">
                                     <textarea rows="5" cols="60" name="remove_reason" id="remove_reason"></textarea>
                                </label>
                    
                                <input type="hidden" value="%(recid)s" name="recid" id="recid">
                                
                                <div class="navigation-bar" id="dialog_actions">
                                    <div class="group right">
                                        <button class="default" type="submit">%(submit_button)s</button>
                                        <button class="close" type="button">%(cancel_button)s</button>
                                    </div>
                                </div>
                            </form>
                        </div>                    
                </div>''' % content_string

    return link + overlay + script

def format(bfo, style):
    """
    Prints a link to BibEdit, if authorization is granted
    @param style the CSS style to be applied to the link.
    """
    _ = gettext_set_language(bfo.lang)
    out = []
    
    if can_edit(bfo):    
        out.append('<a href="/curator/submit/edit?recid=%s&ln=%s">%s</a>' % \
                    (bfo.recID, bfo.lang, _("Edit this record")))
    
    user_info = bfo.user_info
    # before verifing access, assert that the user has a remote_ip and this is not
    # an internal call
    remote_ip = user_info.get('remote_ip', '')    
    
    if remote_ip:
        (auth_code, auth_message) = acc_authorize_action(user_info, 'runbibedit')
        if auth_code == 0:
            out.append('<a href="/record/edit/#state=edit&recid=%s&ln=%s">%s</a>' % \
                    (str(bfo.recID), bfo.lang, _("Edit this record (BibEdit)")))
        
    user_uid = user_info.get('uid')

    if user_uid and not isGuestUser(user_uid):
        out.append(get_ask_for_removal_form(bfo))
        
    out = '&nbsp;&nbsp;|&nbsp;&nbsp;'.join(out)
    
    if remote_ip and auth_code == 0:
        return out + get_pending_informations(bfo) 
    else:
        return out
    
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0