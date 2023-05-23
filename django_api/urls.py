from django.contrib import admin
from django.urls import path, include
from principal.api import UserAPI
from principal.views import Login, Logout, Username
from rest_framework.authtoken import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/create_user/', UserAPI.as_view(), name='create_user'),
    path('principal/', include(('principal.urls', 'principal_urls'))),
    path('api_generate_token/', views.obtain_auth_token),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('api/get_username/', Username.as_view(), name='get_username'),
]
