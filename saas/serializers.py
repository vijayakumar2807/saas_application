from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from .models import *
from djoser.serializers import TokenCreateSerializer
from datetime import date
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

User = get_user_model()

# ✅ Client Serializer
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


# ✅ Client Registration Serializer (Creates Client + User + Subscription + JWT)
# class ClientRegistrationSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#     name = serializers.CharField()
#     plan_id = serializers.IntegerField(write_only=True)

#     class Meta:
#         model = Client
#         fields = ['company_name', 'contact_email', 'industry', 'password', 'name', 'plan_id']

#     def create(self, validated_data):
#         password = validated_data.pop('password')
#         name = validated_data.pop('name')
#         plan_id = validated_data.pop('plan_id')

#         # Create client
#         client = Client.objects.create(**validated_data)

#         # Create main user for client
#         user = User.objects.create(
#             email=client.contact_email,
#             name=name,
#             client=client,
#             is_staff=False
#         )
#         user.set_password(password)
#         user.save()
        

#         # Create subscription
#         Subscription.objects.create(
#             client=client,
#             plan_id=plan_id,
#             start_date=timezone.now().date(),
#             end_date=timezone.now().date() + timezone.timedelta(days=30),
#             status="active"
#         )

#         # Generate JWT tokens
#         refresh = RefreshToken.for_user(user)
#         return {
#             "access": str(refresh.access_token),
#             "refresh": str(refresh),
#             "user_id": user.id,
#             "client_id": client.id
#         }

from rest_framework import serializers
from django.contrib.auth.models import Group
from .models import User
from .models import Subscription  # Make sure you have this import

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    groups = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all(), required=False
    )

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['is_superuser', 'is_staff']
        extra_kwargs = {
            'password': {'write_only': True},
            'client': {'read_only': True},
            'is_superuser': {'read_only': True},
            'is_staff': {'read_only': True},
        }

    def validate(self, attrs):
        request_user = self.context['request'].user

        if not request_user.is_superuser:
            client = request_user.client
            subscription = Subscription.objects.filter(client=client, status='active').order_by('-end_date').first()

            if not subscription:
                raise serializers.ValidationError("No active subscription found.")

            user_limit = subscription.plan.user_limit
            current_users = User.objects.filter(client=client).count()

            if current_users >= user_limit:
                raise serializers.ValidationError(f"User limit of {user_limit} reached. Upgrade your plan.")

        return attrs

    def create(self, validated_data):
        request_user = self.context['request'].user
        groups = validated_data.pop('groups', []) if 'groups' in validated_data else []
        password = validated_data.pop('password')

        if not request_user.is_superuser:
            validated_data['is_superuser'] = False
            validated_data['is_staff'] = False
            validated_data['client'] = request_user.client
            groups = []  # ❌ Prevent clients from assigning groups

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if request_user.is_superuser and groups:
            user.groups.set(groups)

        return user

    def update(self, instance, validated_data):
        request_user = self.context['request'].user
        groups = validated_data.pop('groups', []) if 'groups' in validated_data else []
        password = validated_data.pop('password', None)

        if not request_user.is_superuser:
            validated_data.pop('is_superuser', None)
            validated_data.pop('is_staff', None)
            validated_data['client'] = request_user.client
            groups = []  # ❌ Prevent clients from updating groups

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if request_user.is_superuser and groups:
            instance.groups.set(groups)

        return instance



# ✅ Other Serializers
class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']


# ✅ Custom Token Serializer (extend if needed)
class CustomTokenCreateSerializer(TokenCreateSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # data['user_id'] = self.user.id  # optional extra info
        return data
