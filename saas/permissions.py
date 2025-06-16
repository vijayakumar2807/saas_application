from rest_framework.permissions import BasePermission, SAFE_METHODS

class DynamicModelPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser:
            return True

        try:
            model = getattr(view.queryset, 'model', view.get_queryset().model)
        except Exception:
            return False

        if not model:
            return False

        app_label = model._meta.app_label
        model_name = model._meta.model_name

        if request.method in SAFE_METHODS:
            perm = f"{app_label}.view_{model_name}"
        elif request.method == 'POST':
            perm = f"{app_label}.add_{model_name}"
        elif request.method in ('PUT', 'PATCH'):
            perm = f"{app_label}.change_{model_name}"
        elif request.method == 'DELETE':
            perm = f"{app_label}.delete_{model_name}"
        else:
            return False

        return user.has_perm(perm)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
