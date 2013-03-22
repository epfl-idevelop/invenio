"""BibEdit Templates."""

from invenio.config import CFG_SITE_URL
from invenio.messages import gettext_set_language

from invenio import bibedit_templates
from invenio.bibedit_templates import img, inp, button, link

class Template(bibedit_templates.Template):
    """BibEdit Templates Class."""

    def menu(self):
        """Create the menu."""
        
        recordmenu = """
            <div class="box">
              <h3>Record %(imgNewRecord)s %(imgCloneRecord)s</h3>
              <span id="cellIndicator">%(imgIndicator)s</span><span id="cellStatus">%(lblChecking)s</span>
              <form onsubmit="return false;" style="margin-bottom: 10px;">
                <input type="text" id="txtSearchPattern" class="search" /><select id="sctSearchType" class="search-filter">
                  <option value="recID" selected="selected">Rec ID</option>
                  <option value="reportnumber">Rep No</option>
                  <option value="anywhere">Anywhere</option>
                </select><button class="search-button" id="btnSearch" title="Search">Search</button>
                <div class="clear"></div>
              </form>
                     
              <div id="rowRecordBrowser" style="display: none">
                %(btnPrev)s <span id="cellRecordNo" style="text-align: center">1/1</span> %(btnNext)s
              </div>
              <div id="tickets"><!--filled by bibedit_menu.js--></div>
              <div class="navigation-bar" style="width:324px; margin-top: 10px;">
                <button id="btnSubmit" style="font-weight: bold;" disabled="disabled">Submit</button>
                <button id="btnCancel" disabled="disabled">Cancel</button>
                <button id="btnDeleteRecord" style="float: right;" disabled="disabled">Delete</button>
              </div>
              
              <div class="button question">
                <a href="/help/admin/bibedit-admin-guide" target="_blank">
                  <button class="icon"></button>
                  <span class="label">Help</span>
                </a>
              </div>
            </div>
            
            <div class="box"> 
              <h3>History</h3>
              <div id="bibEditRevisionsHistory"></div>
            
              <h4>Undo / Redo</h4>
              <div class="bibEditURDetailsSection" id="bibEditURUndoListLayer">
                <div class="bibEditURButtonLayer"><button id="btnUndo">&lt;</button></div>
                <div id="undoOperationVisualisationField" class="bibEditHiddenElement bibEditURPreviewBox">
                  <div id="undoOperationVisualisationFieldContent"></div>
                </div>
              </div>
              <div class="bibEditURDetailsSection" id="bibEditURRedoListLayer">
                <div class="bibEditURButtonLayer"><button id="btnRedo">&gt;</button></div>
                <div id="redoOperationVisualisationField" class="bibEditHiddenElement bibEditURPreviewBox">
                  <div id="redoOperationVisualisationFieldContent"></div>
                </div>
              </div>
            </div>""" % {
            'imgIndicator': img('/img/indicator.gif'),
            'lblChecking': 'Checking status' + '...',
            'imgNewRecord': img('/img/table.png', 'bibEditImgCtrlEnabled', id='imgNewRecord', title='New record'),
            'imgCloneRecord': img('/img/table_multiple.png', 'bibEditImgCtrlDisabled', id='imgCloneRecord', title='Clone record'),
            'btnPrev': button('button', 'Previous', id='btnPrev', disabled='disabled'),
            'btnNext': button('button', 'Next', id='btnNext', disabled='disabled'),
            }

        
        viewmenu = """ 
            <div class="navigation-bar" style="width: 652px;">
              <div class="group">View %(btnTagMARC)s %(btnTagNames)s</div>
              <div class="group">Fields 
                <button id="btnAddField" disabled="disabled">Add</button>
                <button id="btnDeleteSelected" disabled="disabled">Delete selected</button>
              </div>
              <div class="group">Switch to
                <button id="btnSwitchReadOnly">Read only</button>
              
              </div>
            </div>""" % {
            'btnTagMARC': button('button', 'MARC', id='btnMARCTags', disabled='disabled'),
            'btnTagNames': button('button', 'Human', id='btnHumanTags', disabled='disabled')
            }

        return """
          <div id="bibEditMenu">
            %(recordmenu)s
          </div>
          <div class="bibedit-options">
            %(viewmenu)s
          </div>
          """ % {
                'recordmenu': recordmenu,
                'viewmenu': viewmenu,
                }

    def history_comparebox(self, ln, revdate, revdate_cmp, comparison):
        """ Display the bibedit history comparison box. """
        _ = gettext_set_language(ln)
        title = '<b>%(comp)s</b><br />%(rev)s %(revdate)s<br />%(rev)s %(revdate_cmp)s' % {
            'comp': _('Comparison of:'),
            'rev': _('Revision'),
            'revdate': revdate,
            'revdate_cmp': revdate_cmp}
        return '''
       <div class="bibEditHistCompare">
         <p>%s</p>
         <p>
           %s
         </p>
       </div>''' % (title, comparison)
