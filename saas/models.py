from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group, Permission
from django.db import models


class Client(models.Model):
    company_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    contact_email = models.EmailField()
    industry = models.CharField(max_length=100)
    password = models.CharField(max_length=128) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # If client is newly created, create a User
        if is_new:
            from django.contrib.auth import get_user_model
            User = get_user_model()

            if not User.objects.filter(email=self.contact_email).exists():
                user = User(
                    email=self.contact_email,
                    client=self,
                    is_staff=False,
                    first_name=self.first_name,
                    last_name=self.last_name,
                )
                user.set_password(self.password)
                user.save()




class CustomUserManager(BaseUserManager):
    def create_user(self, email=None, phone=None, password=None, **extra_fields):
        if not email and not phone:
            raise ValueError("User must have an email or phone number")
        email = self.normalize_email(email) if email else None
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email=email, phone=phone, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    # name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_users',
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_users',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email or self.phone


class Lead(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='leads')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leads')
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    product = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Plan(models.Model):
    name = models.CharField(max_length=40)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    user_limit = models.PositiveSmallIntegerField()
    ai_minutes = models.PositiveIntegerField()
    duration = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=30)
    trial = models.BooleanField(default=False)
    usage = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.client} - {self.plan} ({self.status})"
