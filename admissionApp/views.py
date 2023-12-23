from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from .forms import AddThreadMessageForm, ApplicantSignUpForm, EditReqsForm, EditNurseReqsForm, EditInterviewReqsForm, AddExamSchedForm, EditExamSchedForm
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user
import json
from json import dumps
from django.contrib.auth.models import User as UserModel
import io
from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.lib.pagesizes import letter
from datetime import datetime, date

# ===== Use custom auth_model =======
User = get_user_model()

def index(request):
    return render(request, 'activities/Admission System - Main Window.html')

@unauthenticated_user
def registerPage(request):
    form = ApplicantSignUpForm()

    if request.method == 'POST':
        form = ApplicantSignUpForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Account Successfully Created.')
        else:
            error_string = ''.join([''.join(x for x in l) for l in list(form.errors.values())])
            messages.error(request, str(error_string))

    context = {'form': form}
    return render(request, 'activities/Registration.html', context)

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':    
        user_id = request.POST.get('userid')
        password = request.POST.get('password')
        print(user_id, password)

        user = authenticate(request, username=user_id, password=password)

        if user is not None and user.is_applicant:
            login(request, user)
            return redirect('applicant_home')
        elif user is not None and user.is_tupadmin:
            login(request, user)
            return redirect('tupadmin_home')
        elif user is not None and user.is_interviewer:
            login(request, user)
            return redirect('interviewer_home')
        elif user is not None and user.is_nurse:
            login(request, user)
            return redirect('nurse_home')
        else:
            messages.info(request, 'User ID or Password is incorrect.')

    context = {}
    return render(request, 'activities/Admission System - Main Window.html', context)

def logoutUser(request):
    logout(request)
    return redirect('loginPage')

# ============================== ADMIN ========================================
@login_required(login_url='loginPage')
# ============================== READ ===========================
def admin_perspective_home(request):
    if request.user.is_authenticated and request.user.is_tupadmin:
        pass_status = Applicant_Requirements.objects.filter(main_status='Passed').count()
        ongoing_status = Applicant_Requirements.objects.filter(main_status='On Going').count()
        fail_status = Applicant_Requirements.objects.filter(main_status='Failed').count()
        total_applicants = Applicant_Requirements.objects.all().count()

        count_list = [fail_status, ongoing_status, pass_status]
        data_json = dumps(count_list)

        context = {'pass_count' : pass_status,
                'ongoing_count' : ongoing_status,
                'fail_count' : fail_status,
                'total_count' : total_applicants,
                'count_data' : data_json}
        return render(request, 'activities/Admission Perspective - Home.html', context)
    else:
        if request.user.is_authenticated and request.user.is_applicant:
            return redirect('applicant_home')
        elif request.user.is_authenticated and request.user.is_interviewer:
            return redirect('interviewer_home')
        elif request.user.is_authenticated and request.user.is_nurse:
            return redirect('nurse_home')

@login_required(login_url='loginPage')
def admin_perspective_examschedule(request):
    if request.user.is_authenticated and request.user.is_tupadmin:
        applicants = ExamSchedule.objects.all()

        form = AddExamSchedForm()

        if request.method == "POST":
            form = AddExamSchedForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('tupadmin_examschedule')

        context = {'applicants' : applicants,
                    'form' : form}
        return render(request, 'activities/Admission Perspective - Exam Schedule.html', context)
    else:
        if request.user.is_authenticated and request.user.is_applicant:
            return redirect('applicant_home')
        elif request.user.is_authenticated and request.user.is_interviewer:
            return redirect('interviewer_home')
        elif request.user.is_authenticated and request.user.is_nurse:
            return redirect('nurse_home')

@login_required(login_url='loginPage')
def admin_perspective_update_examsched(request, pk):
    if request.user.is_authenticated and request.user.is_tupadmin:
        exam_sched = ExamSchedule.objects.get(id=pk)
        form = EditExamSchedForm(instance=exam_sched)

        if request.method == "POST":
            form = EditExamSchedForm(request.POST, instance=exam_sched)
            if form.is_valid():
                form.save()
                return redirect('tupadmin_examschedule')

        context = {'form' : form}
        return render(request, 'activities/Admin - Edit Exam Schedule.html', context)
    else:
        if request.user.is_authenticated and request.user.is_applicant:
            return redirect('applicant_home')
        elif request.user.is_authenticated and request.user.is_interviewer:
            return redirect('interviewer_home')
        elif request.user.is_authenticated and request.user.is_nurse:
            return redirect('nurse_home')

@login_required(login_url='loginPage')
def admin_perspective_delete_examsched(request, pk):
    if request.user.is_authenticated and request.user.is_tupadmin:
        exam_sched = ExamSchedule.objects.get(id=pk)

        if request.method == "POST":
            exam_sched.delete()
            return redirect('tupadmin_examschedule')

        context = {'exam' : exam_sched}
        return render(request, 'activities/Admin - Delete Exam Schedule.html', context)
    else:
        if request.user.is_authenticated and request.user.is_applicant:
            return redirect('applicant_home')
        elif request.user.is_authenticated and request.user.is_interviewer:
            return redirect('interviewer_home')
        elif request.user.is_authenticated and request.user.is_nurse:
            return redirect('nurse_home')


@login_required(login_url='loginPage')
def admin_perspective_pdf(request):
    if request.user.is_authenticated and request.user.is_tupadmin:
        context = {}
        return render(request, 'activities/Admission Perspective - Print PDF.html', context)
    else:
        if request.user.is_authenticated and request.user.is_applicant:
            return redirect('applicant_home')
        elif request.user.is_authenticated and request.user.is_interviewer:
            return redirect('interviewer_home')
        elif request.user.is_authenticated and request.user.is_nurse:
            return redirect('nurse_home')

# ============================== READ ===========================
@login_required(login_url='loginPage')
def admin_perspective_applicant_reqs(request):
    if request.user.is_authenticated and request.user.is_tupadmin:
        applicants = Applicant_Requirements.objects.all()

        context = {'applicants': applicants}
        return render(request, 'activities/Admission Perspective - Applicant Requirements.html', context)
    else:
        if request.user.is_authenticated and request.user.is_applicant:
            return redirect('applicant_home')
        elif request.user.is_authenticated and request.user.is_interviewer:
            return redirect('interviewer_home')
        elif request.user.is_authenticated and request.user.is_nurse:
            return redirect('nurse_home')

# ============================ UPDATE ===========================
@login_required(login_url='loginPage')
def update_requirements(request, pk):
    if request.user.is_authenticated and request.user.is_tupadmin:
        appli_reqs = Applicant_Requirements.objects.get(id=pk)
        form = EditReqsForm(instance=appli_reqs)

        if request.method == "POST":
            form = EditReqsForm(request.POST ,instance=appli_reqs)
            if form.is_valid():
                form.save()
                return redirect('tupadmin_applicantreqs')

        context = {'form' : form}
        return render(request, 'activities/Admin - Edit Requirements.html', context)
    else:
        if request.user.is_authenticated and request.user.is_applicant:
            return redirect('applicant_home')
        elif request.user.is_authenticated and request.user.is_interviewer:
            return redirect('interviewer_home')
        elif request.user.is_authenticated and request.user.is_nurse:
            return redirect('nurse_home')

# =========================== DELETE ===========================
@login_required(login_url='loginPage')
def delete_requirements(request, pk):
    if request.user.is_authenticated and request.user.is_tupadmin:
        appli_reqs = Applicant_Requirements.objects.get(id=pk)
        if request.method == "POST":
            appli_reqs.delete()
            return redirect('tupadmin_applicantreqs')

        context = {'applicant' : appli_reqs}
        return render(request, 'activities/Admin - Delete Confirmation.html', context)
    else:
        if request.user.is_authenticated and request.user.is_applicant:
            return redirect('applicant_home')
        elif request.user.is_authenticated and request.user.is_interviewer:
            return redirect('interviewer_home')
        elif request.user.is_authenticated and request.user.is_nurse:
            return redirect('nurse_home')

@login_required(login_url='loginPage')
def admin_perspective_results(request):
    if request.user.is_authenticated and request.user.is_tupadmin:
        return render(request, 'activities/Admission Perspective - View Results.html')
    else:
        if request.user.is_authenticated and request.user.is_applicant:
            return redirect('applicant_home')
        elif request.user.is_authenticated and request.user.is_interviewer:
            return redirect('interviewer_home')
        elif request.user.is_authenticated and request.user.is_nurse:
            return redirect('nurse_home')

# ============================= APPLICANT ====================================
@login_required(login_url='loginPage')
def applicant_perspective_home(request):
    if request.user.is_authenticated and request.user.is_applicant:
        return render(request, 'activities/Applicant Perspective - Home.html')
    else:
        if request.user.is_authenticated and request.user.is_tupadmin:
            return redirect('tupadmin_home')
        elif request.user.is_authenticated and request.user.is_interviewer:
            return redirect('interviewer_home')
        elif request.user.is_authenticated and request.user.is_nurse:
            return redirect('nurse_home')
        

@login_required(login_url='loginPage')
def applicant_perspective_pdf(request):
    if request.user.is_authenticated and request.user.is_applicant:
        if request.method == "POST":
            user_logged = request.user

            buffer = io.BytesIO()

            p = canvas.Canvas(buffer, pagesize=letter)
            p.setFont('Helvetica-Bold', 8)

            # ===== checklist slip =======
            p.drawString(67, 809, f'{user_logged.first_name} {user_logged.applicant.middle_name} {user_logged.last_name}')
            p.drawString(70, 796, f'{user_logged.applicant.appli_course}')
            p.drawString(70, 784, f'{date.today().strftime("%b-%d-%Y")}')

            # ====== interview slip =======
            p.drawString(67, 228, f'{user_logged.first_name} {user_logged.applicant.middle_name} {user_logged.last_name}')
            p.drawString(70, 215, f'{user_logged.applicant.appli_course}')
            p.drawString(70, 203, f'{date.today().strftime("%b-%d-%Y")}')

            # p.drawString(70, 714, '/')
            
            p.save()
            buffer.seek(0)

            new_pdf = PdfFileReader(buffer)
            existing_pdf = PdfFileReader(open('admissionApp/static/Media/slip.pdf', "rb"))

            page = existing_pdf.getPage(0)
            page.mergePage(new_pdf.getPage(0))

            output = PdfFileWriter()
            output.addPage(page)
            output_stream = open("admissionApp/static/Media/new_slip.pdf", "wb")
            output.write(output_stream)
            output_stream.close()

            with open('admissionApp/static/Media/new_slip.pdf', 'rb') as pdf:
                response = HttpResponse(pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename=pre-admission_checklist.pdf'
                return response

        else:
            return render(request, 'activities/Applicant Perspective - Print PDF.html')
    else:
        if request.user.is_authenticated and request.user.is_tupadmin:
            return redirect('tupadmin_home')
        elif request.user.is_authenticated and request.user.is_interviewer:
            return redirect('interviewer_home')
        elif request.user.is_authenticated and request.user.is_nurse:
            return redirect('nurse_home')

@login_required(login_url='loginPage')
def applicant_perspective_results(request):
    if request.user.is_authenticated and request.user.is_applicant:
        return render(request, 'activities/Applicant Perspective  - View Results.html')
    else:
        if request.user.is_authenticated and request.user.is_tupadmin:
            return redirect('tupadmin_home')
        elif request.user.is_authenticated and request.user.is_interviewer:
            return redirect('interviewer_home')
        elif request.user.is_authenticated and request.user.is_nurse:
            return redirect('nurse_home')

# =================================== INTERVIEWER ==================================
# ============================== READ ===========================
@login_required(login_url='loginPage')
def interviewer_perspective_home(request):
    if request.user.is_authenticated and request.user.is_interviewer:
        pass_status = Applicant_Requirements.objects.filter(inter_status='Passed').count()
        ongoing_status = Applicant_Requirements.objects.filter(inter_status='On Going').count()
        fail_status = Applicant_Requirements.objects.filter(inter_status='Failed').count()
        total_applicants = Applicant_Requirements.objects.all().count()

        count_list = [fail_status, ongoing_status, pass_status]
        data_json = dumps(count_list)

        context = {'pass_count' : pass_status,
                'ongoing_count' : ongoing_status,
                'fail_count' : fail_status,
                'total_count' : total_applicants,
                'count_data' : data_json}
        return render(request, 'activities/Interviewer Perspective - Home.html', context)
    else:
        if request.user.is_authenticated and request.user.is_tupadmin:
            return redirect('tupadmin_home')
        elif request.user.is_authenticated and request.user.is_applicant:
            return redirect('applicant_home')
        elif request.user.is_authenticated and request.user.is_nurse:
            return redirect('nurse_home')

# ========== Interviwer Read ============
@login_required(login_url='loginPage')
def interviewer_perspective_result(request):
    if request.user.is_authenticated and request.user.is_interviewer:
        applicants = Applicant_Requirements.objects.all()

        context = {'applicants' : applicants}
        return render(request, 'activities/Interviewer Perspective - View Results.html', context)
    else:
        if request.user.is_authenticated and request.user.is_tupadmin:
            return redirect('tupadmin_home')
        elif request.user.is_authenticated and request.user.is_applicant:
            return redirect('applicant_home')
        elif request.user.is_authenticated and request.user.is_nurse:
            return redirect('nurse_home')

# =========================== UPDATE ===========================
@login_required(login_url='loginPage')
def inter_update_requirements(request, pk):
    if request.user.is_authenticated and request.user.is_interviewer:
        appli_reqs = Applicant_Requirements.objects.get(id=pk)
        form = EditInterviewReqsForm(instance=appli_reqs)

        if int(appli_reqs.score) < 75:
            form.fields['inter_status'].disabled = True
        else:
            form.fields['inter_status'].disabled = False

        if request.method == "POST":
            form = EditInterviewReqsForm(request.POST ,instance=appli_reqs)
            if form.is_valid():
                form.save()
                return redirect('interviewer_result')

        context = {'form' : form,
                'applicant_score' : int(appli_reqs.score)}
        return render(request, 'activities/Interviewer - Edit Requirements.html', context)
    else:
        if request.user.is_authenticated and request.user.is_tupadmin:
            return redirect('tupadmin_home')
        elif request.user.is_authenticated and request.user.is_applicant:
            return redirect('applicant_home')
        elif request.user.is_authenticated and request.user.is_nurse:
            return redirect('nurse_home')

@login_required(login_url='loginPage')
def interviewer_perspective_pdf(request):
    if request.user.is_authenticated and request.user.is_interviewer:
        return render(request, 'activities/Interviewer Perspective - Print PDF.html')
    else:
        if request.user.is_authenticated and request.user.is_tupadmin:
            return redirect('tupadmin_home')
        elif request.user.is_authenticated and request.user.is_applicant:
            return redirect('applicant_home')
        elif request.user.is_authenticated and request.user.is_nurse:
            return redirect('nurse_home')

# =============================== NURSE =====================================
# ============================== READ ===========================
@login_required(login_url='loginPage')
def nurse_perspective_home(request):
    if request.user.is_authenticated and request.user.is_nurse:
        pass_status = Applicant_Requirements.objects.filter(medical_status='Passed').count()
        ongoing_status = Applicant_Requirements.objects.filter(medical_status='On Going').count()
        fail_status = Applicant_Requirements.objects.filter(medical_status='Failed').count()
        total_applicants = Applicant_Requirements.objects.all().count()

        count_list = [fail_status, ongoing_status, pass_status]
        data_json = dumps(count_list)

        context = {'pass_count' : pass_status,
                'ongoing_count' : ongoing_status,
                'fail_count' : fail_status,
                'total_count' : total_applicants,
                'count_data' : data_json}
        return render(request, 'activities/Nurse Perspective - Home.html', context)
    else:
        if request.user.is_authenticated and request.user.is_tupadmin:
            return redirect('tupadmin_home')
        elif request.user.is_authenticated and request.user.is_applicant:
            return redirect('applicant_home')
        elif request.user.is_authenticated and request.user.is_interviewer:
            return redirect('interviewer_home')
    
# ============================== READ ===========================
@login_required(login_url='loginPage')
def nurse_perspective_result(request):
    if request.user.is_authenticated and request.user.is_nurse:
        applicants = Applicant_Requirements.objects.all()

        context = {'applicants' : applicants}
        return render(request, 'activities/Nurse Perspective - View Results.html', context)
    else:
        if request.user.is_authenticated and request.user.is_tupadmin:
            return redirect('tupadmin_home')
        elif request.user.is_authenticated and request.user.is_applicant:
            return redirect('applicant_home')
        elif request.user.is_authenticated and request.user.is_interviewer:
            return redirect('interviewer_home')

# =========================== UPDATE ===========================
@login_required(login_url='loginPage')
def nurse_update_requirements(request, pk):
    if request.user.is_authenticated and request.user.is_nurse:
        appli_reqs = Applicant_Requirements.objects.get(id=pk)
        form = EditNurseReqsForm(instance=appli_reqs)

        if appli_reqs.inter_status == 'Pending' or appli_reqs.inter_status == 'On Going' or appli_reqs.inter_status == 'Failed':
            form.fields['medical_status'].disabled = True
        else:
            form.fields['medical_status'].disabled = False

        if request.method == "POST":
            form = EditNurseReqsForm(request.POST ,instance=appli_reqs)
            
            if form.is_valid():
                form.save()
                return redirect('nurse_result')

        context = {'form' : form,
                'applicant' : appli_reqs}
        return render(request, 'activities/Nurse - Edit Requirements.html', context)
    else:
        if request.user.is_authenticated and request.user.is_tupadmin:
            return redirect('tupadmin_home')
        elif request.user.is_authenticated and request.user.is_applicant:
            return redirect('applicant_home')
        elif request.user.is_authenticated and request.user.is_interviewer:
            return redirect('interviewer_home')

@login_required(login_url='loginPage')
def nurse_perspective_pdf(request):
    if request.user.is_authenticated and request.user.is_nurse:
        return render(request, 'activities/Nurse Perspective - Print PDF.html')
    else:
        if request.user.is_authenticated and request.user.is_tupadmin:
            return redirect('tupadmin_home')
        elif request.user.is_authenticated and request.user.is_applicant:
            return redirect('applicant_home')
        elif request.user.is_authenticated and request.user.is_interviewer:
            return redirect('interviewer_home')
    
# ====== New messaging function ============
@login_required(login_url='loginPage')
def admission_perspective_message(request):
    form = AddThreadMessageForm(request.user)

    if request.method == "POST":
        form = AddThreadMessageForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('tupadmin_compose')

    threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
    context = {
        'Threads': threads,
        'form' : form
    }
    return render(request, 'activities/Admission Perspective - Message.html', context)

@login_required(login_url='loginPage')
def applicant_perspective_message(request):
    form = AddThreadMessageForm(request.user)

    if request.method == "POST":
        form = AddThreadMessageForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('applicant_compose')
    threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
    context = {
        'Threads': threads,
        'form' : form
    }
    return render(request, 'activities/Applicant Perspective - Message.html', context)

@login_required(login_url='loginPage')
def interviewer_perspective_message(request):  
    form = AddThreadMessageForm(request.user)

    if request.method == "POST":
        form = AddThreadMessageForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('interviewer_compose')
    threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
    context = {
        'Threads': threads,
        'form' : form
    }
    return render(request, 'activities/Interviewer Perspective - Message.html', context)

@login_required(login_url='loginPage')
def nurse_perspective_message(request):
    form = AddThreadMessageForm(request.user)

    if request.method == "POST":
        form = AddThreadMessageForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('nurse_compose')
    threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
    context = {
        'Threads': threads,
        'form' : form
    }
    return render(request, 'activities/Nurse Perspective - Message.html', context)