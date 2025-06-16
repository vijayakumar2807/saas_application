from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from .models import *
from djoser.serializers import TokenCreateSerializer
from datetime import date
User = get_user_model()

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'



class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    groups = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all(), required=False
    )

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['is_superuser', 'is_staff']

    def validate(self, attrs):
        request_user = self.context['request'].user

        if not request_user.is_superuser:
            client = request_user.client
            active_sub = client.subscriptions.filter(status='active').order_by('-end_date').first()
            if not active_sub:
                raise serializers.ValidationError("No active subscription found.")
            if active_sub.end_date < date.today() or client.users.filter(is_active=True).count() >= active_sub.plan.user_limit:
                raise serializers.ValidationError("Plan expired or user limit exceeded.")
        return attrs

    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password')
        request_user = self.context['request'].user

        if not request_user.is_superuser:
            validated_data['is_superuser'] = False
            validated_data['is_staff'] = False
            validated_data['client'] = request_user.client

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if groups:
            user.groups.set(groups)
        return user

    def update(self, instance, validated_data):
        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password', None)
        request_user = self.context['request'].user

        if not request_user.is_superuser:
            validated_data.pop('is_superuser', None)
            validated_data.pop('is_staff', None)
            validated_data['client'] = request_user.client

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()

        if groups:
            instance.groups.set(groups)
        return instance   
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['is_superuser', 'is_staff']

    def validate(self, attrs):
        request_user = self.context['request'].user

        if not request_user.is_superuser:
            client = request_user.client
            active_sub = client.subscriptions.filter(status='active').order_by('-end_date').first()

            if not active_sub:
                raise serializers.ValidationError("No active subscription found. Please subscribe to a plan.")

            user_limit = active_sub.plan.user_limit
            current_users = client.users.filter(is_active=True).count()
            today = date.today()

            if current_users >= user_limit or active_sub.end_date < today:
                raise serializers.ValidationError(
                    "Your plan has expired or user limit reached. Please upgrade your plan."
                )

        return attrs

    def create(self, validated_data):
        request_user = self.context['request'].user

        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password')

        if not request_user.is_superuser:
            validated_data['is_superuser'] = False
            validated_data['is_staff'] = False
            validated_data['client'] = request_user.client

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if groups:
            user.groups.set(groups)

        return user

    def update(self, instance, validated_data):
        request_user = self.context['request'].user

        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password', None)

        if not request_user.is_superuser:
            validated_data.pop('is_superuser', None)
            validated_data.pop('is_staff', None)
            validated_data['client'] = request_user.client

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if groups:
            instance.groups.set(groups)

        return instance
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['is_superuser', 'is_staff']

    def validate(self, attrs):
        request_user = self.context['request'].user

        if not request_user.is_superuser:
            client = request_user.client
            active_sub = client.subscriptions.filter(status='active').order_by('-end_date').first()

            if not active_sub:
                raise serializers.ValidationError("No active subscription found. Please subscribe to a plan.")

            user_limit = active_sub.plan.user_limit
            current_users = client.users.filter(is_active=True).count()
            today = date.today()

            if current_users >= user_limit or active_sub.end_date < today:
                raise serializers.ValidationError(
                    "Your plan has expired or user limit reached. Please upgrade your plan."
                )

        return attrs

    def create(self, validated_data):
        request_user = self.context['request'].user

        # Handle many-to-many 'groups' separately
        groups = validated_data.pop('groups', [])

        password = validated_data.pop('password')

        if not request_user.is_superuser:
            validated_data['is_superuser'] = False
            validated_data['is_staff'] = False
            validated_data['client'] = request_user.client

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Set many-to-many after save
        if groups:
            user.groups.set(groups)

        return user

    def update(self, instance, validated_data):
        request_user = self.context['request'].user

        # Handle many-to-many 'groups' separately
        groups = validated_data.pop('groups', [])

        password = validated_data.pop('password', None)

        if not request_user.is_superuser:
            validated_data.pop('is_superuser', None)
            validated_data.pop('is_staff', None)
            validated_data['client'] = request_user.client

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        # Set many-to-many after save
        if groups:
            instance.groups.set(groups)

        return instance
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['is_superuser', 'is_staff']

    def validate(self, attrs):
        request_user = self.context['request'].user

        if not request_user.is_superuser:
            client = request_user.client
            active_sub = client.subscriptions.filter(status='active').order_by('-end_date').first()

            if not active_sub:
                raise serializers.ValidationError("No active subscription found. Please subscribe to a plan.")

            user_limit = active_sub.plan.user_limit
            current_users = client.users.filter(is_active=True).count()
            today = date.today()

            if current_users >= user_limit or active_sub.end_date < today:
                raise serializers.ValidationError(
                    "Your plan has expired or user limit reached. Please upgrade your plan."
                )

        return attrs

    def create(self, validated_data):
        request_user = self.context['request'].user

        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password')

        if not request_user.is_superuser:
            validated_data['is_superuser'] = False
            validated_data['is_staff'] = False
            validated_data['client'] = request_user.client

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if groups:
            user.groups.set(groups)

        return user

    def update(self, instance, validated_data):
        request_user = self.context['request'].user

        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password', None)

        if not request_user.is_superuser:
            validated_data.pop('is_superuser', None)
            validated_data.pop('is_staff', None)
            validated_data['client'] = request_user.client

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if groups:
            instance.groups.set(groups)

        return instance

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['is_superuser', 'is_staff']

    def validate(self, attrs):
        request_user = self.context['request'].user

        # Only restrict clients (not superusers)
        if not request_user.is_superuser:
            client = request_user.client
            active_sub = client.subscriptions.filter(status='active').order_by('-end_date').first()

            if not active_sub:
                raise serializers.ValidationError("No active subscription found. Please subscribe to a plan.")

            user_limit = active_sub.plan.user_limit
            current_users = client.users.filter(is_active=True).count()
            today = date.today()

            # 🔴 Combined condition for expiration or user limit breach
            if current_users >= user_limit or active_sub.end_date < today:
                raise serializers.ValidationError(
                    f"Your plan has expired or user limit reached. Please upgrade your plan."
                )

        return attrs
        
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['is_superuser', 'is_staff']  # prevent client from sending these directly



    def create(self, validated_data):
        request_user = self.context['request'].user

        # Always force is_superuser and is_staff = False for client users
        if not request_user.is_superuser:
            validated_data['is_superuser'] = False
            validated_data['is_staff'] = False
            validated_data['client'] = request_user.client  # enforce ownership
        # If superuser: allow full flexibility (but could still validate)

        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user

    def update(self, instance, validated_data):
        request_user = self.context['request'].user

        if not request_user.is_superuser:
            # Prevent client users from elevating privileges
            validated_data.pop('is_superuser', None)
            validated_data.pop('is_staff', None)
            validated_data['client'] = request_user.client

        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


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


class CustomTokenCreateSerializer(TokenCreateSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # You can add more info here if needed:
        # data['user_id'] = self.user.id
        return data