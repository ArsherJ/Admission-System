from django.urls import path

from . import views

urlpatterns = [
    path('registration/', views.registerPage, name='registration'),
    path('', views.loginPage, name='loginPage'),
    path('logout', views.logoutUser, name='logout'),

    # ======= ADMIN PERSPECTIVE ==========
    path('tupadmin/home', views.admin_perspective_home, name='tupadmin_home'),
    path('tupadmin/examination_schedule', views.admin_perspective_examschedule, name='tupadmin_examschedule'),
    path('tupadmin/edit_examschedule/<str:pk>/', views.admin_perspective_update_examsched, name='tupadmin_editexam'),
    path('tupadmin/delete_examschedule/<str:pk>/', views.admin_perspective_delete_examsched, name='tupadmin_deleteexam'),
    path('tupadmin/pdf', views.admin_perspective_pdf, name='tupadmin_pdf'),
    path('tupadmin/applicant_requirements', views.admin_perspective_applicant_reqs, name='tupadmin_applicantreqs'),
    path('tupadmin/edit_requirement/<str:pk>/', views.update_requirements, name='tupadmin_editreqs'),              
    path('tupadmin/delete_requirement/<str:pk>/', views.delete_requirements, name='tupadmin_deletereqs'),           
    
    # ======= APPLICANT PERSPECTIVE ==========
    path('applicant/home', views.applicant_perspective_home, name='applicant_home'),
    path('applicant/result', views.applicant_perspective_results, name='applicant_result'),
    path('applicant/pdf', views.applicant_perspective_pdf, name='applicant_pdf'),

    #======= INTERVIWER PERSPECTIVE ==========
    path('interviewer/home', views.interviewer_perspective_home, name='interviewer_home'),
    path('interviewer/result', views.interviewer_perspective_result, name='interviewer_result'),
    path('interviewer/edit_result/<str:pk>/', views.inter_update_requirements, name='interviewer_editreqs'),
    path('interviewer/pdf', views.interviewer_perspective_pdf, name='interviewer_pdf'),

    #======= NURSE PERSPECTIVE ==========
    path('nurse/home', views.nurse_perspective_home, name='nurse_home'),
    path('nurse/results', views.nurse_perspective_result, name='nurse_result'),
    path('nurse/edit_result/<str:pk>/', views.nurse_update_requirements, name='nurse_editreqs'),
    path('nurse/pdf', views.nurse_perspective_pdf, name='nurse_pdf'),

    # ========== NEW MESSAGING ==========
    path('tupadmin/message/', views.admission_perspective_message, name='tupadmin_compose'),
    path('applicant/message/', views.applicant_perspective_message, name='applicant_compose'),
    path('interviewer/message/', views.interviewer_perspective_message, name='interviewer_compose'),
    path('nurse/message/', views.nurse_perspective_message, name='nurse_compose'),
]