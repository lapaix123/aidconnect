from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, BeneficiaryViewSet, CaseViewSet, CaseNoteViewSet,
    AssessmentViewSet, AssessmentQuestionViewSet, AssessmentAnswerViewSet,
    dashboard_redirect, admin_dashboard, case_manager_dashboard, field_officer_dashboard,
    login_view, BeneficiaryListView, BeneficiaryDetailView, BeneficiaryCreateView,
    BeneficiaryUpdateView, BeneficiaryDeleteView,
    CaseListView, CaseDetailView, CaseCreateView, CaseUpdateView, CaseDeleteView,
    AssessmentListView, AssessmentDetailView, AssessmentCreateView, AssessmentUpdateView, AssessmentDeleteView,
    CaseNoteListView, CaseNoteDetailView, CaseNoteCreateView, CaseNoteUpdateView, CaseNoteDeleteView,
    VisitListView
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
    path('api/', include(router.urls)),

    # Authentication
    path('', login_view, name='login'),  # Root URL serves the login page
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Dashboards
    path('dashboard/', dashboard_redirect, name='dashboard_redirect'),
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/case-manager/', case_manager_dashboard, name='case_manager_dashboard'),
    path('dashboard/field-officer/', field_officer_dashboard, name='field_officer_dashboard'),

    # Beneficiary Management
    path('beneficiaries/', BeneficiaryListView.as_view(), name='beneficiary_list'),
    path('beneficiaries/add/', BeneficiaryCreateView.as_view(), name='beneficiary_create'),
    path('beneficiaries/<int:pk>/', BeneficiaryDetailView.as_view(), name='beneficiary_detail'),
    path('beneficiaries/<int:pk>/edit/', BeneficiaryUpdateView.as_view(), name='beneficiary_update'),
    path('beneficiaries/<int:pk>/delete/', BeneficiaryDeleteView.as_view(), name='beneficiary_delete'),

    # Case Management
    path('cases/', CaseListView.as_view(), name='case_list'),
    path('cases/add/', CaseCreateView.as_view(), name='case_create'),
    path('cases/<int:pk>/', CaseDetailView.as_view(), name='case_detail'),
    path('cases/<int:pk>/edit/', CaseUpdateView.as_view(), name='case_update'),
    path('cases/<int:pk>/delete/', CaseDeleteView.as_view(), name='case_delete'),

    # Assessment Management
    path('assessments/', AssessmentListView.as_view(), name='assessment_list'),
    path('assessments/add/', AssessmentCreateView.as_view(), name='assessment_create'),
    path('assessments/<int:pk>/', AssessmentDetailView.as_view(), name='assessment_detail'),
    path('assessments/<int:pk>/edit/', AssessmentUpdateView.as_view(), name='assessment_update'),
    path('assessments/<int:pk>/delete/', AssessmentDeleteView.as_view(), name='assessment_delete'),

    # Case Note Management
    path('case-notes/', CaseNoteListView.as_view(), name='case_note_list'),
    path('case-notes/add/', CaseNoteCreateView.as_view(), name='case_note_create'),
    path('case-notes/<int:pk>/', CaseNoteDetailView.as_view(), name='case_note_detail'),
    path('case-notes/<int:pk>/edit/', CaseNoteUpdateView.as_view(), name='case_note_update'),
    path('case-notes/<int:pk>/delete/', CaseNoteDeleteView.as_view(), name='case_note_delete'),

    # Visit Management (for Field Officers)
    path('visits/', VisitListView.as_view(), name='visit_list'),
]
