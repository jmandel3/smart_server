"""
Middleware (filters) for SMArt (inspired by Indivo)

inspired by django.contrib.auth middleware, but doing it differently
for tighter integration into email-centric users in Indivo.
"""

import re
import smart

from time import strftime
from django.http import *
from django.core.exceptions import PermissionDenied
from django.conf import settings

from smart import accesscontrol

class Authorization(object):

  def process_view(self, request, view_func, view_args, view_kwargs):
    """ The process_view() hook allows us to examine the request before view_func is called"""
   
    # Url exception(s)
    exc_pattern= settings.SMART_ACCESS_CONTROL_EXCEPTION
    if exc_pattern and re.match(exc_pattern, request.path):
      return None

    if hasattr(view_func, 'resolve'):
      view_func = view_func.resolve(request)

    try:
      if view_func:
        permission_set = self.get_permset(request)
        access_rule = self.get_accessrule(view_func)

        # given a set of permissions, and a rule for access checking
        # apply the rules to the permission set with the current request parameters
        if permission_set and access_rule:
          if access_rule.check(permission_set, view_args, view_kwargs):
            return None

        # otherwise, this will fail
    except:
      raise PermissionDenied
    raise PermissionDenied

  def get_permset(self, request):
    if request.principal:
      return request.principal.permset
    else:
      return smart.accesscontrol.PermissionSetType().nouser()

  def get_accessrule(self, view_func):
    return accesscontrol.get_accessrule(view_func)

# Mark that the authorization module has been loaded
# nothing gets served otherwise
smart.AUTHORIZATION_MODULE_LOADED = True