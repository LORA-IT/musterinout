
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager


ROLE_TYPE = (
    ('Manager',"Manager"),
    ('HR',"HR"),
    ('Employee',"Employee")
)
 
class CustomUser(AbstractUser):
    username = None
    role = models.CharField(choices=ROLE_TYPE, max_length=100, error_messages={'required': "Role must be provided"})
    employee_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=254, unique=True)
 
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
 
    USERNAME_FIELD = "employee_id"
    REQUIRED_FIELDS = ['email']
 
    def __unicode__(self):
        return self.employee_id
 
    objects = UserManager()




from django.conf import settings

class Attendance(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)


    class Meta:
        unique_together = ('employee', 'date')  # Ensures one record per employee per day


    def __str__(self):
        return f"{self.employee.employee_id} - {self.date}"
