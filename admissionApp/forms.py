from django.contrib.auth.forms import UserCreationForm, UsernameField
from django import forms
from django.db.models import fields
from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.forms import widgets
from django.forms.models import model_to_dict
from django.forms.widgets import PasswordInput
from django.db import transaction
from .models import Applicant, Applicant_Requirements, ChatMessage, ExamSchedule, Thread
from django.contrib.auth import get_user_model
from datetime import datetime
import uuid
from django.core.mail import send_mail
from django.db.models import Q

User = get_user_model()

class ApplicantSignUpForm(UserCreationForm):
    USER_SEX = [('Male', 'Male'),
                ('Female', 'Female')]

    STRAND = [('STEM', 'Science, Technology, Engineering, and Mathematics'),
              ('ABM', 'Accountancy, Business, and Management'),
              ('HUMSS', 'Humanities and Social Sciences'),
              ('TECH-VOC', 'Technical-Vocational-Livelihood'),
              ('GAS', 'General Academic Strand')]
    
    APPLI_COURSE = [('BS-CE', 'Bachelor of Science in Civil Engineering'),
                    ('BS-EE', 'Bachelor of Science in Electrical Engineering'),
                    ('BS-ECE', 'Bachelor of Science in Electronics Engineering'),
                    ('BS-ME', 'Bachelor of Science in Mechanical Engineering'),
                    ('BET-MT', 'Bachelor of Engineering Technology major in Mechanical Technology'),
                    ('BET-COET', 'Bachelor of Engineering Technology major in Computer Engineering Technology'),
                    ('BET-CT', 'Bachelor of Engineering Technology major in Civil Technology'),
                    ('BET-MT', 'Bachelor of Engineering Technology major in Mechanical Technology'),
                    ('BET-MT', 'Bachelor of Engineering Technology major in Mechanical Technology'),
                    ('BET-MT', 'Bachelor of Engineering Technology major in Mechanical Technology'),]

    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class' : 'form-control', 'placeholder': 'Enter your first name'}))
    middle_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class' : 'form-control', 'placeholder': 'Enter your middle name'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class' : 'form-control', 'placeholder': 'Enter your last name'}))
    sex = forms.CharField(label="Sex:", widget=forms.Select(choices=USER_SEX, attrs={'class' : 'form-select form-select-md'}))
    emailaddress = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class' : 'form-control', 'placeholder': 'Enter your email address'}))
    birthday = forms.DateField(required=True, widget=forms.widgets.DateInput(attrs={'type': 'date', 'class' : 'form-control'}))
    address = forms.CharField(required=True, widget=forms.TextInput(attrs={'class' : 'form-control', 'placeholder': 'Enter your address'}))
    mobilenumber = forms.CharField(required=True, widget=forms.TextInput(attrs={'class' : 'form-control', 'placeholder': 'Enter your mobile number'}))
    course = forms.CharField(label="Course:", widget=forms.Select(choices=APPLI_COURSE, attrs={'class' : 'form-select form-select-md'}))
    strand = forms.CharField(label="Strand:", widget=forms.Select(choices=STRAND, attrs={'class' : 'form-select form-select-md'}))
    password1 = forms.CharField(widget=PasswordInput(attrs={'class' : 'form-control', 'placeholder':'Enter your Password'}))
    password2 = forms.CharField(widget=PasswordInput(attrs={'class' : 'form-control', 'placeholder':'Password Confirmation'}))
    username = forms.CharField(required=False)
    class Meta(UserCreationForm.Meta):
        model = User
    
    # ================= CREATE ==================
    def save(self):
        
        date_now = datetime.now()
        unique_id = str(uuid.uuid4().int)

        user_id = f"{self.cleaned_data.get('last_name')}-{str(date_now.year)[2:]}-{unique_id[:4]}"

        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name')
        user.middle_name = self.cleaned_data.get('middle_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('emailaddress')
        user.username = user_id
        user.is_applicant = True
        user.save()
        
        appli = Applicant.objects.create(user=user)
        appli.appli_sex = self.cleaned_data.get('sex')
        appli.middle_name = self.cleaned_data.get('middle_name')
        appli.appli_birthday = str(self.cleaned_data.get('birthday'))
        appli.appli_address = self.cleaned_data.get('address')
        appli.appli_mobilenumber = self.cleaned_data.get('mobilenumber')
        appli.appli_course = self.cleaned_data.get('course')
        appli.appli_strand = self.cleaned_data.get('strand')
        appli.save()

        appli_reqs = Applicant_Requirements.objects.create(user_appli=appli)
        appli_reqs.score = 0
        appli_reqs.card = False
        appli_reqs.barangay_clearance = False
        appli_reqs.good_moral = False
        appli_reqs.psa_birthcert = False
        appli_reqs. medical_status = 'On Going'
        appli_reqs. inter_status = 'On Going'
        appli_reqs. main_status = 'On Going'
        appli_reqs.save()
       

        send_mail('Registration Successful',
            f"""Congratulations you are now registered. Please double check your registration.\n
        Here's your username: {user_id}
        Name: {user.first_name} {user.middle_name} {user.last_name}
        Email: {user.email}
        Birthday: {appli.appli_birthday}
        Address: {appli.appli_address}
        Mobile Number: {appli.appli_mobilenumber}
        Applied Course: {appli.appli_course}
        SHS Strand: {appli.appli_strand}""",
            
            'admission.system123@gmail.com',
            [f'{user.email}'],
            fail_silently=False)

        return user

# ========= TUPADMIN ==========
class EditReqsForm(ModelForm):
    class Meta:
        model = Applicant_Requirements
        fields = ['score', 'card', 'barangay_clearance', 'good_moral', 'psa_birthcert', 'main_status']
        widgets = {
            'score' : forms.TextInput(attrs={'class' : 'form validate', 'type' : 'number'}),
            'card' : forms.CheckboxInput(attrs={'class' : 'form-check-input', 'type' : 'checkbox'}),
            'barangay_clearance' : forms.CheckboxInput(attrs={'class' : 'form-check-input', 'type' : 'checkbox'}),
            'good_moral' : forms.CheckboxInput(attrs={'class' : 'form-check-input', 'type' : 'checkbox'}),
            'psa_birthcert' : forms.CheckboxInput(attrs={'class' : 'form-check-input', 'type' : 'checkbox'}),
            'main_status' : forms.Select(attrs={'class' : 'form-select form-select-md'}),
        }
    
    def save(self):
        appli_reqs = super(EditReqsForm, self).save(commit=False)

        if int(self.cleaned_data.get('score')) < 75:
            appli_reqs.inter_status = 'Failed'
            appli_reqs.medical_status = 'Failed'
            appli_reqs.main_status = 'Failed'
            appli_reqs.save()
        else:
            appli_reqs.inter_status = 'On Going'
            appli_reqs.medical_status = 'Pending'
            appli_reqs.main_status = 'Pending'
            appli_reqs.save()

        return appli_reqs

# ===== INTERVIEWER ======
class EditInterviewReqsForm(ModelForm):
    class Meta:
        model = Applicant_Requirements
        fields = ['inter_status']
        widgets = {
            'inter_status' : forms.Select(attrs={'class' : 'form-select form-select-md'}),
        }
    
    def save(self):
        appli_reqs = super(EditInterviewReqsForm, self).save(commit=False)

        if appli_reqs.inter_status == 'On Going':
            appli_reqs.medical_status = 'Pending'
            appli_reqs.main_status = 'Pending'
            appli_reqs.save()
        elif appli_reqs.inter_status == 'Failed':
            appli_reqs.medical_status = 'Failed'
            appli_reqs.main_status = 'Failed'
            appli_reqs.save()
        elif appli_reqs.inter_status == 'Passed':
            appli_reqs.medical_status = 'On Going'
            appli_reqs.main_status = 'Pending'
            appli_reqs.save()
        else:
            appli_reqs.medical_status = 'Pending'
            appli_reqs.main_status = 'Pending'
            appli_reqs.save()

        return appli_reqs

# ===== NURSE =====
class EditNurseReqsForm(ModelForm):
    class Meta:
        model = Applicant_Requirements
        fields = ['medical_status']
        widgets = {
            'medical_status' : forms.Select(attrs={'class' : 'form-select form-select-md'}),
        }
    
    def save(self):
        appli_reqs = super(EditNurseReqsForm, self).save(commit=False)

        if appli_reqs.medical_status == 'On Going':
            appli_reqs.main_status = 'Pending'
            appli_reqs.save()
        elif appli_reqs.medical_status == 'Failed':
            appli_reqs.main_status = 'Failed'
            appli_reqs.save()
        elif appli_reqs.medical_status == 'Passed':
            appli_reqs.main_status = 'Passed'
            appli_reqs.save()
        else:
            appli_reqs.main_status = 'Pending'
            appli_reqs.save()
            
        return appli_reqs


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=200)
    last_name = forms.CharField(max_length=200)

    class Meta:
        model = User
        fields = ['first_name','last_name','username','email','password1','password2']

# ====== Exam Schedule =======
class AddExamSchedForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddExamSchedForm, self).__init__(*args, **kwargs)

        inner_qs = ExamSchedule.objects.values_list('examiner', flat=True)
        results = Applicant.objects.exclude(user__in=inner_qs)

        self.fields['examiner'].queryset = results
        
    class Meta:
        model = ExamSchedule
        fields = ['examiner', 'exam_date', 'exam_time', 'room']
        
        widgets = {
            'examiner' : forms.Select(attrs={'class' : 'form-select form-select-md'}),
            'exam_date' : forms.widgets.DateInput(attrs={'type': 'date', 'class' : 'form-control'}),
            'exam_time' : forms.widgets.TimeInput(attrs={'class' : 'form-control', 'type' : 'time'}),
            'room' : forms.TextInput(attrs={'class' : 'form-control validate', 'type' : 'number'}),
        }
    def save(self, commit=True):
        exam = super(AddExamSchedForm, self).save(commit=False)
        exam.examiner = self.cleaned_data.get('examiner')
        exam.exam_date = self.cleaned_data.get('exam_date')
        exam.exam_time = self.cleaned_data.get('exam_time')
        exam.room = self.cleaned_data.get('room')

        if commit:
            exam.save()
        
        return exam

class EditExamSchedForm(ModelForm):
    class Meta:
        model = ExamSchedule
        fields = ['exam_date', 'exam_time', 'room']
        
        widgets = {
            'exam_date' : forms.widgets.DateInput(attrs={'type': 'date', 'class' : 'form-control'}),
            'exam_time' : forms.widgets.TimeInput(attrs={'class' : 'form-control', 'type' : 'time'}),
            'room' : forms.TextInput(attrs={'class' : 'form-control validate', 'type' : 'number'}),
        }

class AddThreadMessageForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AddThreadMessageForm, self).__init__(*args, **kwargs)

        thread_qs = Thread.objects.filter(Q(first_person=self.user.id) | Q(second_person=self.user.id))

        innerqs = thread_qs.values_list('first_person', flat=True)
        innerqs1 = thread_qs.values_list('second_person', flat=True)

        results = User.objects.exclude(Q(id__in=innerqs) | Q(id__in=innerqs1) | Q(id__in=[self.user.id,]))

        self.fields['second_person'].queryset = results

    class Meta:
        model = Thread
        fields = ['second_person']
        widgets = {
            'second_person' : forms.Select(attrs={'class' : 'form-select form-select-md'}),
        }

    def save(self, commit=True):
        thread = super(AddThreadMessageForm, self).save(commit=False)
        thread.first_person = self.user
        thread.second_person = self.cleaned_data.get('second_person')

        if commit:
            thread.save()
        
        return thread