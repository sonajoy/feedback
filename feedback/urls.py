from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeedbackViewSet, add_feedback, custom_login, delete_feedback, feedback_list
from . import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Feedback API",
        default_version='v1',
        description="API for managing feedback",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@yourdomain.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

router = DefaultRouter()

router.register(r'feedback', FeedbackViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('register/', views.register, name='register'),#signup
     path('', views.home, name='home'),
    path('login/', custom_login, name='login'),#login
    path('logout/', views.logout_view, name='logout'), #logout
    path('dashboard/', views.user_dashboard, name='user_dashboard'),  # User Dashboard
    path('feedback/add/', views.add_feedback, name='add_feedback'),   # Add Feedback
    path('feedback-list/', feedback_list, name='feedback-list'),#user feedback list
    path('feedback/update/<int:feedback_id>/', views.update_feedback, name='update_feedback'),
    path('feedback/delete/<int:feedback_id>/', views.delete_feedback, name='delete_feedback'), 
    path('auditor-dashboard/', views.auditor_dashboard, name='auditor_dashboard'),#auditor dashboard
    path('verify-feedback/<int:feedback_id>/', views.verify_feedback, name='verify_feedback'),#auditor feedback verification
    path('delete-feedback/<int:feedback_id>/', views.delete_feedback_auditor, name='delete_feedback'),#auditor feedback deletion

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-docs'),#endpoint documentation
]