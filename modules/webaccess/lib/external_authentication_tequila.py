# -*- coding: utf-8 -*-
"""External user authentication trough Tequila for Invenio.
   User is authenticated trough Tequila, but user's informations are retrieved trough LDAP
"""

from invenio.external_authentication import ExternalAuth, InvenioWebAccessExternalAuthError
from invenio.webgroup_dblayer import get_group_id

from django_tequila.tequila_client import TequilaClient, EPFLConfig

import ldap

CFG_EXTERNAL_AUTH_LDAP_SERVERS = ['ldap://scoldap.epfl.ch']
CFG_EXTERNAL_AUTH_LDAP_CONTEXT = "o=EPFL,c=CH"
CFG_EXTERNAL_AUTH_LDAP_USER_UID  = ["uid", "uniqueIdentifier", "mail"]
CFG_EXTERNAL_AUTH_LDAP_MAIL_ENTRY = 'mail'
CFG_EXTERNAL_AUTH_LDAP_GROUP_MEMBERSHIP = 'memberOf'
CFG_EXTERNAL_AUTH_LDAP_GROUP_UID = 'uniqueIdentifier'
CFG_EXTERNAL_AUTH_LDAP_GROUP_NAME = 'displayName'

CFG_EXTERNAL_AUTH_LDAP_HIDDEN_GROUPS = ['EPFL-unit', 'users']

class TequilaExternalAuth(ExternalAuth):
    def __init__(self):
        """Initialize stuff here"""
        self.name = "EPFL"
        # Set the following variable to True in order to import the externally
        # provided nickname into Invenio during the first login of a user
        # through this external authentication system.
        # If the nickname is already taken into Invenio, then it won't be
        # considered.
        self.enforce_external_nicknames = True
        
    def _ldap_try (self, command):
        """ Try to run the specified command on the first LDAP server that
        is not down."""    
        for server in CFG_EXTERNAL_AUTH_LDAP_SERVERS:
            try:
                connection = ldap.initialize(server)
                return command(connection)
            except ldap.SERVER_DOWN, error_message:
                continue
        raise InvenioWebAccessExternalAuthError        
        
    def auth_user(self, username, password, req=None):
        """Authenticate user-supplied USERNAME and PASSWORD.  Return
        None if authentication failed, or the email address of the
        person if the authentication was successful.  In order to do
        this you may perhaps have to keep a translation table between
        usernames and email addresses.
        Raise InvenioWebAccessExternalAuthError in case of external troubles.
        """
        """step done after we come back from the tequila process.
           we should have the tequila key as username, and password should
           be at None
        """
        try:
            tequila_client = TequilaClient(EPFLConfig(allow_guests=True))
            
            user_attributes = tequila_client.get_attributes(username)
            
            return user_attributes['email']
        except:
            # if we cannot get the user attributes, take it as a fail
            return None
        
    def user_exists(self, email, req=None):
        """Check the external authentication system for existance of email.
        @return True if the user exists, False otherwise
        """
        query = '(%s=%s)' % (CFG_EXTERNAL_AUTH_LDAP_MAIL_ENTRY, email)
        def _check (connection):
            users = connection.search_s(CFG_EXTERNAL_AUTH_LDAP_CONTEXT, 
                                        ldap.SCOPE_SUBTREE, 
                                        query)
            return len(users) != 0
        return self._ldap_try(_check)
    
    def fetch_user_nickname(self, username, password, req=None):
        """Given a username and a password, returns the right nickname belonging
        to that user (username could be an email).
        """    
        query = '(|' + ''.join (['(%s=%s)' % (attrib, username) 
                                 for attrib in 
                                     CFG_EXTERNAL_AUTH_LDAP_USER_UID]) \
                 + ')'
        def _get_nickname(connection):
            users = connection.search_s(CFG_EXTERNAL_AUTH_LDAP_CONTEXT, 
                                        ldap.SCOPE_SUBTREE, 
                                        query)    
            # We pick the first result, as all the data we are interested
            # in should be the same in all the entries.
            if len(users):
                user_dn, user_info = users [0]
            else:
                return None
            emails = user_info[CFG_EXTERNAL_AUTH_LDAP_MAIL_ENTRY]
            if len(emails):
                email = emails[0]
            else:
                return False
            (left_part, right_part) = email.split('@')
            nickname = left_part.replace('.', ' ').title()
            if right_part != 'epfl.ch':
                nickname += ' - ' + right_part
            return nickname
        return self._ldap_try(_get_nickname)

    def fetch_user_groups_membership(self, username, password, req=None):
        """Given a username and a password, returns a dictionary of groups
        and their description to which the user is subscribed.
        Raise WebAccessExternalAuthError in case of troubles.
        """
        query_person = '(|' + ''.join (['(%s=%s)' % (attrib, username) 
                                 for attrib in 
                                     CFG_EXTERNAL_AUTH_LDAP_USER_UID]) \
                        + ')'
        def _get_groups(connection):
            users = connection.search_s(CFG_EXTERNAL_AUTH_LDAP_CONTEXT, 
                                        ldap.SCOPE_SUBTREE, 
                                        query_person)
            if len(users):
                user_dn, user_info = users [0]
            else:
                return {}
            groups = {}
            
            try:
                group_ids = user_info[CFG_EXTERNAL_AUTH_LDAP_GROUP_MEMBERSHIP]
            except KeyError:
                return None
            
            for group_id in group_ids:
                query_group = '(%s=%s)' % (CFG_EXTERNAL_AUTH_LDAP_GROUP_UID,
                                           group_id)
                ldap_group = connection.search_s(CFG_EXTERNAL_AUTH_LDAP_CONTEXT,
                                                 ldap.SCOPE_SUBTREE, 
                                                 query_group)
                if len(ldap_group):
                    group_dn, group_infos = ldap_group[0]
                    group_name = group_infos[CFG_EXTERNAL_AUTH_LDAP_GROUP_NAME][0]
                    if group_name in CFG_EXTERNAL_AUTH_LDAP_HIDDEN_GROUPS:
                        continue
                    groups[group_id] = group_name
            return groups
        return self._ldap_try(_get_groups)
    
    def fetch_user_preferences(self, username, password=None, req=None):
        """Given a username and a password, returns a dictionary of keys and
        values, corresponding to external infos and settings.

        userprefs = {"telephone": "2392489",
                     "address": "10th Downing Street"}

        (WEBUSER WILL erase all prefs that starts by EXTERNAL_ and will
        store: "EXTERNAL_telephone"; all internal preferences can use whatever
        name but starting with EXTERNAL). If a pref begins with HIDDEN_ it will
        be ignored.
        """
        query = '(|' + ''.join (['(%s=%s)' % (attrib, username) 
                                 for attrib in 
                                     CFG_EXTERNAL_AUTH_LDAP_USER_UID]) \
                 + ')'
        def _get_personal_infos(connection):
            users = connection.search_s(CFG_EXTERNAL_AUTH_LDAP_CONTEXT, 
                                        ldap.SCOPE_SUBTREE, 
                                        query)
            if len(users):
                user_dn, user_info = users [0]
                return user_info
            else:
                return {}
        return self._ldap_try(_get_personal_infos)