
from rest_framework import viewsets, permissions,serializers
from django.contrib.auth.models import Group, Permission
from .models import Client, Lead, Plan, Subscription, User
from .serializers import *
from .permissions import DynamicModelPermission
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.views import APIView,Response,status
from rest_framework.exceptions import PermissionDenied


# class ClientUserCreateView(viewsets.ModelViewSet):
#     serializer_class = UserSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return User.objects.filter(client=self.request.user.client)

#     def perform_create(self, serializer):
#         client = self.request.user.client

#         try:
#             subscription = Subscription.objects.filter(client=client, status='active').latest('start_date')
#         except Subscription.DoesNotExist:
#             raise PermissionDenied("No active subscription found.")

#         user_limit = subscription.plan.user_limit
#         current_user_count = User.objects.filter(client=client).count()

#         if current_user_count >= user_limit:
#             raise PermissionDenied(f"User limit reached ({user_limit}). Upgrade your plan.")

#         serializer.save(client=client)

# class ClientRegistrationView(APIView):
#     authentication_classes = []
#     permission_classes = []

#     def post(self, request):
#         serializer = ClientRegistrationSerializer(data=request.data)
#         if serializer.is_valid():
#             data = serializer.save()
#             return Response(data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    




class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [AllowAny]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        return User.objects.filter(client=user.client)

    def perform_create(self, serializer):
        request_user = self.request.user
        if request_user.is_superuser:
            serializer.save()
        else:
            serializer.save(client=request_user.client, is_superuser=False, is_staff=False)

    @action(detail=True, methods=['post'])
    def assign_permissions(self, request, pk=None):
        user = self.get_object()
        permissions_ids = request.data.get('permissions', [])

        if not request.user.is_superuser:
            allowed_permissions = Permission.objects.filter(codename__in=[
                "view_lead", "add_lead", "change_lead", "delete_lead",
                "view_user", "add_user", "change_user"
            ])
            requested_permissions = Permission.objects.filter(id__in=permissions_ids)
            invalid = set(requested_permissions) - set(allowed_permissions)
            if invalid:
                return Response({"detail": "Not allowed to assign some permissions."}, status=403)

        user.user_permissions.set(permissions_ids)
        return Response({"detail": "Permissions updated"})

class LeadViewSet(viewsets.ModelViewSet):
    queryset=Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated, DynamicModelPermission]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Lead.objects.all()
        return Lead.objects.filter(client=user.client)

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated, DynamicModelPermission]

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset=Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, DynamicModelPermission]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Subscription.objects.all()
        return Subscription.objects.filter(client=user.client)

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated, DynamicModelPermission]

class PermissionViewSet(viewsets.ModelViewSet):
    queryset=Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated, DynamicModelPermission]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Permission.objects.all()
        return Permission.objects.filter(codename__startswith='view_')  # or filter down further
