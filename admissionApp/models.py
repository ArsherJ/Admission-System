from typing import Tuple
from django.db import models
from django.db.models import Model
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models import Q


# Create your models here.
class User(AbstractUser):
    is_applicant = models.BooleanField(default=False)
    is_tupadmin = models.BooleanField(default=False)
    is_interviewer = models.BooleanField(default=False)
    is_nurse = models.BooleanField(default=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

class Applicant(Model):
    USER_SEX = [('Male', 'Male'),
                ('Female', 'Female')]

    STRAND = [('STEM', 'Science, Technology, Engineering, and Mathematics'),
              ('ABM', 'Accountancy, Business, and Management'),
              ('HUMSS', 'Humanities and Social Sciences'),
              ('TECH-VOC', 'Technical-Vocational-Livelihood'),
              ('GAS', 'General Academic Strand')]
    
    APPLI_COURSE = [('BGT-AT', 'Bachelor in Graphics Technology major in Architecture Technology'),
                    ('BET-ET', 'Bachelor of Engineering Technology major in Electrical Technology'),
                    ('BET-ESET', 'Bachelor of Engineering Technology major in Electronics Technology'),
                    ('BET-COET', 'Bachelor of Engineering Technology major in Computer Engineering Technology'),
                    ('BET-CT', 'Bachelor of Engineering Technology major in Civil Technology'),
                    ('BET-MT', 'Bachelor of Engineering Technology major in Mechanical Technology'),
                    ('BET-AT', 'Bachelor of Engineering Technology major in Automotive Technology'),
                    ('BET-PPT', 'Bachelor of Engineering Technology major in Power Plant Technology'),
                    ('BSIE-IA', 'Bachelor of Science in Industrial Education major in Industrial Arts'),
                    ('BSIE-ICT', 'Bachelor of Science in Industrial Education major in Information and Communication Technology'),
                    ('BSCE', 'Bachelor of Science in Civil Engineering'),
                    ('BSEE', 'Bachelor of Science in Electrical Engineering'),
                    ('BSME', 'Bachelor of Science in Mechanical Engineering')
                    ]

    user = models.OneToOneField(User, on_delete=CASCADE, primary_key=True)
    middle_name = models.CharField(max_length=100)
    appli_sex = models.CharField(max_length=100, choices=USER_SEX)
    appli_birthday = models.DateField(null=True, blank=True)
    appli_address = models.CharField(max_length=100)
    appli_mobilenumber = models.CharField(max_length=20)
    appli_course = models.CharField(max_length=100, choices=APPLI_COURSE)
    appli_strand = models.CharField(max_length=100, choices=STRAND)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Applicant_Requirements(Model):
    MED_STATUS = [('On Going', 'On Going'),
                  ('Passed', 'Passed'),
                  ('Failed', 'Failed'),
                  ('Pending', 'Pending')]

    INT_STATUS = [('On Going', 'On Going'),
                  ('Passed', 'Passed'),
                  ('Failed', 'Failed'),
                  ('Pending', 'Pending')]
    
    MAIN_STATUS = [('On Going', 'On Going'),
                  ('Passed', 'Passed'),
                  ('Failed', 'Failed'),
                  ('Pending', 'Pending')]

    user_appli = models.OneToOneField(Applicant, on_delete=CASCADE)
    score = models.CharField(max_length=10)
    card = models.BooleanField(default=False)
    barangay_clearance = models.BooleanField(default=False)
    good_moral = models.BooleanField(default=False)
    psa_birthcert = models.BooleanField(default=False)
    medical_status = models.CharField(max_length=100, choices=MED_STATUS, blank=False, null=False, default='Pending')
    inter_status = models.CharField(max_length=100, choices=INT_STATUS, blank=False, null=False, default='Pending')
    main_status = models.CharField(max_length=100, choices=MAIN_STATUS, blank=False, null=False, default='Pending')

    def __str__(self):
        return f"{self.user_appli.user.first_name} {self.user_appli.user.last_name}"

class ExamSchedule(Model):
    examiner = models.OneToOneField(Applicant, on_delete=CASCADE)
    exam_date = models.DateField(null=True, blank=True)
    exam_time = models.TimeField(null=True, blank=True)
    room = models.CharField(max_length=20)


    def __str__(self):
        return f"{self.examiner.user.first_name} {self.examiner.user.last_name}"


class ThreadManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        lookup = Q(first_person=user) | Q(second_person=user)
        qs = self.get_queryset().filter(lookup).distinct()
        return qs


class Thread(Model):
    first_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='thread_first_person')
    second_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='thread_second_person')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()
    class Meta:
        unique_together = ['first_person', 'second_person']


class ChatMessage(Model):
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.CASCADE, related_name='chatmessage_thread')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)