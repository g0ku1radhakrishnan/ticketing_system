from django.contrib import admin
from django.urls import path
from.import views


urlpatterns = [
    path('',views.login),






    path('admin_home',views.admin_home),
    path('admin_manage_tailor', views.admin_manage_tailor, name='admin_manage_tailor'), 
    path('admin_update_tailor/<id>', views.admin_update_tailor, name='admin_update_tailor'),
    path('admin_delete_tailor/<id>', views.admin_delete_tailor, name='admin_delete_tailor'),
    path('admin_manage_cutter', views.admin_manage_cutter, name='admin_manage_cutter'),
    path('admin_update_cutter/<id>', views.admin_update_cutter, name='admin_update_cutter'),
    path('admin_delete_cutter/<id>', views.admin_delete_cutter, name='admin_delete_cutter'),
    path('admin_manage_customer',views.admin_manage_customer,name='admin_manage_customer'),
    path('admin_update_customer/<id>',views.admin_update_customer,name='admin_manage_customer'),
    path('admin_delete_customer/<id>',views.admin_delete_customer,name='admin_manage_customer'),
    path('customer_search_suggestions/', views.customer_search_suggestions, name='customer_search_suggestions'),
    path('admin_manage_ticket',views.admin_manage_ticket,name='admin_manage_ticket'),
    path('admin_update_ticket/<id>',views.admin_update_ticket,name='admin_update_ticket'),
    path('admin_delete_ticket/<id>',views.admin_delete_ticket,name='admin_delete_ticket'),
    path('admin_manage_measurement',views.admin_manage_measurement,name='admin_manage_measurement'),
    path('get_customer_measurements/', views.get_customer_measurements, name='get_customer_measurements'),
    path('admin_total_orders/', views.admin_total_orders, name='admin_total_orders'),
    path('admin_active_orders/', views.admin_active_orders, name='admin_active_orders'),
    path('admin_completed_orders/', views.admin_completed_orders, name='admin_completed_orders'),
    path('admin_search/', views.admin_search, name='admin_search'),
    path('admin_urgent_orders/', views.admin_urgent_orders, name='admin_urgent_orders'),
    path('admin_delete_measurement/<id>',views.admin_delete_measurement,name='admin_delete_measurement'),
    path('admin_update_measurement/<id>',views.admin_update_measurement,name='admin_update_measurement'),




   
]