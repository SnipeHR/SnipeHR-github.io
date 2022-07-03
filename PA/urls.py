"""PA URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path,re_path

from website import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mycandidate', views.my_candidate, name='my_candidate'),
    path('', views.index, name='index'),
    path('log', views.log, name='log'),
    path('log_error', views.log_error, name='log_error'),
    path('log_form', views.log_form, name='log_form'),
    path('login_form', views.login_form, name='login_form'),
    path('home', views.home, name='home'),
    path('user_profile', views.user_profile, name='user_profile'),
    path('my_posts', views.my_posts, name="my_posts"),
    path('candidats', views.candidats, name="candidats"),
    path('post_generator', views.post_generator, name='post_generator'),
    path('post_generated', views.post_generated, name='post_generated'),
    path('post_valid', views.post_valid, name='post_valid'),
    path('upload_post', views.upload_post, name='upload_post'),
    path('faq', views.faq, name='faq'),
    path('pages-contact', views.pages_contact, name='pages-contact'),
    path('historic', views.historic, name='historic'),
    path('messagerie', views.messagerie, name='messagerie'),
    path('cv_details', views.cv_details, name='cv_details'),
    #path('my_candidate', views.my_candidate, name='my_candidate'),
    path('my_candidate/<str:name_hr>/<str:url_desc>/upload_cv', views.upload_cv, name='upload_cv'),
    path('my_candidate/<str:name_hr>/<str:url_desc>/', views.my_candidate)
]
