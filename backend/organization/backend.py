from django.contrib.auth.backends import BaseBackend
from organization.models import Organization, OrgAdmin
from django.contrib.auth.hashers import check_password

class OrganizationBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            organization = Organization.objects.get(email=email)
            if organization and check_password(password, organization.user.password):
                return organization.user  # Assuming Organization has a related `user`
        except Organization.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return Organization.objects.get(user__id=user_id).user
        except Organization.DoesNotExist:
            return None

class AdminUserBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            admin_user = OrgAdmin.objects.get(email=email)
            if admin_user and check_password(password, admin_user.password):
                return admin_user
        except OrgAdmin.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return OrgAdmin.objects.get(pk=user_id)
        except OrgAdmin.DoesNotExist:
            return None
