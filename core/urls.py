from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, BeneficiaryViewSet, CaseViewSet, CaseNoteViewSet,
    AssessmentViewSet, AssessmentQuestionViewSet, AssessmentAnswerViewSet,
    dashboard_redirect, admin_dashboard, case_manager_dashboard, field_officer_dashboard
)

# API Router
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'beneficiaries', BeneficiaryViewSet)
router.register(r'cases', CaseViewSet)
router.register(r'case-notes', CaseNoteViewSet)
router.register(r'assessments', AssessmentViewSet)
router.register(r'assessment-questions', AssessmentQuestionViewSet)
router.register(r'assessment-answers', AssessmentAnswerViewSet)

# URL patterns
urlpatterns = [
    # API endpoints - these will be included under /api/ in the main urls.py
    path('', include(router.urls)),

    # Authentication
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Dashboards
    path('', dashboard_redirect, name='dashboard_redirect'),
    path('dashboard/', dashboard_redirect, name='dashboard'),
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/case-manager/', case_manager_dashboard, name='case_manager_dashboard'),
    path('dashboard/field-officer/', field_officer_dashboard, name='field_officer_dashboard'),
]
