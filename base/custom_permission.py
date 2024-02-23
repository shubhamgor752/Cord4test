from rest_framework.permissions import BasePermission
from rest_framework.exceptions import APIException




class CustomPermissionDenied(APIException):
    status_code = 403
    default_code = "custom_permission_error"

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = "Please, Enable your location"
        self.args = (detail,)
        self.code = code or self.default_code
        self.detail = detail

    def get_full_details(self):
        return {"message": str(self.detail)}

class LocationPermission(BasePermission):
    def has_permission(self, request, view):
        if (
            request.session.get("current_cell_id")
            and request.session.get("longitude")
            and request.session.get("latitude")
        ):
            return True

        raise CustomPermissionDenied()
