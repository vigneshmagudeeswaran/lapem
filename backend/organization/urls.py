from django.urls import path

from . import views

urlpatterns = [
   
    path('create', views.create_organization, name='create_organization'),
    path('get_organization/<int:pk>', views.get_organization, name='get_organization'),
    path('organization/password_setup/<int:pk>/', views.password_setup, name='password_setup'),
    # path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("auth/callback/", views.callback, name="callback"),
]
