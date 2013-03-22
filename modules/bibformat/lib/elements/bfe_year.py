# -*- coding: utf-8 -*-
"""BibFormat element - Print year of publication
"""
def format(bfo):
    if bfo.field('260__c'):
        return bfo.field('260__c')