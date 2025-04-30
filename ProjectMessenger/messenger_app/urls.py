from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *


urlpatterns = [
    path("register/", register_view, name="register"),
    path("", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path('profile/', profile_view, name='profile'),
    path("profile/edit/", profile_edit_view, name="profile_edit"),
    path('find_partner/', find_partner_view, name='find_partner'),
    path('chat/<int:chat_id>/', chat_view, name='chat'),
    path('chat/<int:chat_id>/leave/', leave_chat_view, name='leave_chat'),
    path('check_chat/', check_chat_status, name='check_chat'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)