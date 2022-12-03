
from django.db.models import *;
from django.contrib.auth.models import *;

# Create your models here.
###############################################################################

class SystemUser(User):
    ci = CharField(max_length=11)
    phone = CharField(max_length=10)
    age = IntegerField()
    sex = CharField(max_length=1, default='M')
    icon_path = CharField(max_length=128, default='img/profiles/default_profile.png')
    
class SystemUserManager:    
    
    def get_system_user(self, user : User):
        return self.objects.get(id=user.id)
    
###############################################################################
    
class Worker(SystemUser):
    role = CharField(max_length=20)
    
    
class WorkerManager:
    
    # check if an instance of user is a Worker
    def is_worker_user(user : User) -> bool :
        
        try:
            return Worker.objects.get(id=user.id) is not None
        except Worker.DoesNotExist:
            return False
    
    def get_worker_user(user : User):
        
        try:
            return Worker.objects.get(id=user.id)
        except Worker.DoesNotExist:
            return None
    
    def list_all():
        return Worker.objects.values()

###############################################################################
class Patient(SystemUser):
    blod_group = CharField(max_length=3)

class PatientManager:
    
    # check if an instance of user is a Patient
    def is_patient_user( user : User) -> bool :
        
        try:
            return Patient.objects.get(id=user.id) is not None
        except Patient.DoesNotExist:
            return False
    
    def get_patient_user(user : User):
        
        try:
            return Patient.objects.get(id=user.id)
        except Patient.DoesNotExist:
            return None
    
    def list_all():
        return Patient.objects.values()

###############################################################################

#Test management model class
class Test(Model):
    patient = ForeignKey(Patient, on_delete=CASCADE, null=True)
    testID = CharField(max_length=11)
    result = CharField(max_length=256)
    begin_date = DateField()
    resolution_date = DateField()

class TestManager:    
    
    def list_all():
        return Test.objects.values()

###############################################################################

#Event management model class
class SystemEvent(Model):
    date = DateField()
    type = CharField(max_length=32, default="NOTICE")
    message = CharField(max_length=512)
    
class UserEvent(SystemEvent):
    user = ForeignKey(User, on_delete=CASCADE)
    

class EventManager:    
    
    def list_all_events():
        return SystemEvent.objects.values()
        
    def list_all_user_events():
        return UserEvent.objects.values()

    # check if an instance of event is a UserEvent
    def is_user_event(user : User) -> bool :
        return UserEvent.objects.get(id=user.id) is not None
    
    