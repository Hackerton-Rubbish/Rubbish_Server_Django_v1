from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from imagekit.models import ProcessedImageField


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password=None, nickname='익명', **extra_fields):
        if not email:
            raise ValueError('No Email.')
        email = self.normalize_email(email)
        user = self.model(email=email, password=password, nickname=nickname, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, email, password=None, nickname='익명', **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, nickname, **extra_fields)

    def create_superuser(self, email, password, nickname='Admin', **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Administrator must be 'is_staff' is True")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Administrator must be 'is_superuser' is True")

        return self._create_user(email, password, nickname, **extra_fields)


class emailAuth(models.Model):
    mail = models.EmailField(verbose_name='Mail Sender', max_length=255, unique=True, primary_key=True)
    authCode = models.CharField(verbose_name='Auth', max_length=8, unique=False)
    requestTime = models.DateTimeField(verbose_name='RequestedTime', default=timezone.now)
    isAuthed = models.BooleanField(default=False)


class User(AbstractUser):
    objects = UserManager()
    primaryKey = models.BigAutoField(verbose_name='pk', db_column='pk', primary_key=True)
    email = models.EmailField(verbose_name='email', max_length=255, unique=True, primary_key=False)
    nickname = models.CharField(max_length=8, default='익명', null=False, unique=True)
    profileImgURL = models.ImageField(verbose_name='profile Image', upload_to='v1', null=True, default='v1/default/profile.jpg')
    region = models.CharField(max_length=50, default='서울', null=False, blank=True)

    USERNAME_FIELD = 'nickname'
    REQUIRED_FIELDS = ['email']
    date_joined = models.DateTimeField('date joined', default=timezone.now)

    def __str__(self):
        return self.email

    def get_short_name(self):
        return self.nickname

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'


class userInfo(models.Model):
    primaryKey = models.BigAutoField(verbose_name='pk', db_column='pk', primary_key=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=False, blank=False)
    role = models.CharField(max_length=10, default='리사이클러', null=False, blank=True)
    kakaoID = models.CharField(max_length=50, default='', null=False, blank=True)
    openChat = models.TextField(default='', null=False)
    instagram = models.CharField(max_length=30, default='', null=False, blank=True)
    about = models.TextField(default='', null=False)


class garbage_output(models.Model):
    primaryKey = models.BigAutoField(verbose_name='pk', db_column='pk', primary_key=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=False, blank=False)
    date_year = models.IntegerField(null=False, blank=True)
    date_month = models.IntegerField(null=False, blank=True)
    amount = models.IntegerField(default=0, null=False, blank=True, unique=False)


class marketPost(models.Model):
    primaryKey = models.BigAutoField(verbose_name='pk', db_column='pk', primary_key=True)
    author = models.ForeignKey("User", on_delete=models.CASCADE, null=False, blank=False)
    postKind = models.CharField(max_length=10, default='sell', null=False, blank=True)
    trashKind = models.CharField(max_length=30, default='기타', null=False, blank=True)
    content = models.TextField(default='', null=False, blank=True)
    qty = models.IntegerField(default=0, blank=False, null=False, unique=False)
    location = models.CharField(max_length=30, default='', null=False, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

class marketPostImage(models.Model):
    primaryKey = models.BigAutoField(verbose_name='pk', db_column='pk', primary_key=True)
    order = models.IntegerField(verbose_name='image_order', null=False, blank=True)
    postModel = models.ForeignKey("marketPost", on_delete=models.CASCADE, null=False, blank=False)
    image = ProcessedImageField(upload_to='v1', null=True, format='JPEG', options={'quality': 90})


class artPost(models.Model):
    primaryKey = models.BigAutoField(verbose_name='pk', db_column='pk', primary_key=True)
    author = models.ForeignKey("User", on_delete=models.CASCADE, null=False, blank=False)
    title = models.CharField(max_length=40, default='제목', null=False, blank=True)
    content = models.TextField(default='', null=False, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

class artPostImage(models.Model):
    primaryKey = models.BigAutoField(verbose_name='pk', db_column='pk', primary_key=True)
    order = models.IntegerField(verbose_name='image_order', null=False, blank=True)
    postModel = models.ForeignKey("artPost", on_delete=models.CASCADE, null=False, blank=False)
    image = ProcessedImageField(upload_to='v1', null=True, format='JPEG', options={'quality': 90})

