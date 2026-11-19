from django.urls import path
from . import views

urlpatterns = [

    path('cutter_home',views.cutter_home),
    path('tailor_home',views.tailor_home),
    path('cutter_home/', views.cutter_home, name='cutter_dashboard'),
    path('cutter_available_jobs/', views.cutter_available_jobs, name='cutter_available_jobs'),
    path('cutter_completed_jobs/', views.cutter_completed_jobs, name='cutter_completed_jobs'),    path('cutter_my_jobs/', views.cutter_my_jobs, name='cutter_my_jobs'),
    path('claim_ticket/<id>', views.claim_ticket, name='claim_ticket'),
    path('update_cutting_status/<id>', views.update_cutting_status, name='update_cutting_status'),
    path('tailor_home/', views.tailor_home, name='tailor_dashboard'),
    path('tailor_available_jobs/', views.tailor_available_jobs, name='tailor_available_jobs'),
    path('tailor_my_jobs/', views.tailor_my_jobs, name='tailor_my_jobs'),
    path('tailor_claim_ticket/<id>', views.tailor_claim_ticket, name='tailor_claim_ticket'),
    path('update_tailoring_status/<id>', views.update_tailoring_status, name='update_tailoring_status'),
    path('tailor_completed_jobs/', views.tailor_completed_jobs, name='tailor_completed_jobs'),

]