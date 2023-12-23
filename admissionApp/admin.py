from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import User, Applicant, Applicant_Requirements, ExamSchedule, ChatMessage, Thread
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('is_applicant', 
                                                                'is_tupadmin', 
                                                                'is_interviewer', 
                                                                'is_nurse')}),)

    add_fieldsets = UserAdmin.add_fieldsets + ((None, {'fields': ('is_applicant', 
                                                                'is_tupadmin', 
                                                                'is_interviewer', 
                                                                'is_nurse')}),)

# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(Applicant)
admin.site.register(Applicant_Requirements)
admin.site.register(ExamSchedule)
admin.site.register(ChatMessage)

class ChatMessage(admin.TabularInline):
    model = ChatMessage


class ThreadForm(forms.ModelForm):
    def clean(self):
        
        super(ThreadForm, self).clean()
        first_person = self.cleaned_data.get('first_person')
        second_person = self.cleaned_data.get('second_person')
        lookup1 = Q(first_person=first_person) & Q(second_person=second_person)
        lookup2 = Q(first_person=second_person) & Q(second_person=first_person)
        lookup = Q(lookup1 | lookup2)
        
        qs = Thread.objects.filter(lookup)
        if qs.exists():
            raise ValidationError(f'Thread between {first_person} and {second_person} already exists.')

class ThreadAdmin(admin.ModelAdmin):
    # inlines = [ChatMessage]
    class Meta:
        model = Thread

admin.site.register(Thread, ThreadAdmin)