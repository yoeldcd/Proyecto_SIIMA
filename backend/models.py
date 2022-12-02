
from django.db.models import *;
from django.contrib.auth.models import *;

# Create your models here.

class SystemUser(User):
    ci = CharField(max_length=11)
    phone = CharField(max_length=10)
    age = IntegerField()
    
class Worker(SystemUser):
    role = CharField(max_length=20)
        
class Patient(SystemUser):
    blod_group = CharField(max_length=3)

#Test management model class
class Test(Model):
    patientCI = CharField(max_length=11)
    #patientCI = ForeignKey(Patient.ci, on_delete=CASCADE)
    testID = CharField(max_length=11)
    result = CharField(max_length=256)
    begin_date = DateField()
    resolution_date = DateField()

#Event management model class
class SystemEvent(Model):
    date = DateField()
    message = CharField(max_length=512)

class UserEvent(SystemEvent):
    user = ForeignKey(User, on_delete=CASCADE)