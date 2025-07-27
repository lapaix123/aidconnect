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
    VisitListView,ProgramViewSet, BeneficiaryCategoryViewSet, ProgramListView, ProgramDetailView, ProgramCreateView, ProgramUpdateView, ProgramDeleteView,
    BeneficiaryCategoryListView, BeneficiaryCategoryDetailView, BeneficiaryCategoryCreateView,
    BeneficiaryCategoryUpdateView, BeneficiaryCategoryDeleteView,
    # Report views
    ReportTemplateListView, ReportTemplateDetailView, ReportTemplateCreateView, 
    ReportTemplateUpdateView, ReportTemplateDeleteView, ReportListView, 
    ReportDetailView, ReportCreateView, ReportUpdateView, ReportDeleteView,
    generate_report, generate_custom_report,
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
# 👉 New registrations
router.register(r'programs', ProgramViewSet)
router.register(r'categories', BeneficiaryCategoryViewSet)

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
    # Programs
    path('programs/', ProgramListView.as_view(), name='program_list'),
    path('programs/add/', ProgramCreateView.as_view(), name='program_create'),
    path('programs/<int:pk>/', ProgramDetailView.as_view(), name='program_detail'),
    path('programs/<int:pk>/edit/', ProgramUpdateView.as_view(), name='program_update'),
    path('programs/<int:pk>/delete/', ProgramDeleteView.as_view(), name='program_delete'),

    # Categories
    path('categories/', BeneficiaryCategoryListView.as_view(), name='category_list'),
    path('categories/add/', BeneficiaryCategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/', BeneficiaryCategoryDetailView.as_view(), name='category_detail'),
    path('categories/<int:pk>/edit/', BeneficiaryCategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', BeneficiaryCategoryDeleteView.as_view(), name='category_delete'),

    # Report Templates
    path('report-templates/', ReportTemplateListView.as_view(), name='report_template_list'),
    path('report-templates/add/', ReportTemplateCreateView.as_view(), name='report_template_create'),
    path('report-templates/<int:pk>/', ReportTemplateDetailView.as_view(), name='report_template_detail'),
    path('report-templates/<int:pk>/edit/', ReportTemplateUpdateView.as_view(), name='report_template_update'),
    path('report-templates/<int:pk>/delete/', ReportTemplateDeleteView.as_view(), name='report_template_delete'),

    # Reports
    path('reports/', ReportListView.as_view(), name='report_list'),
    path('reports/add/', ReportCreateView.as_view(), name='report_create'),
    path('reports/<int:pk>/', ReportDetailView.as_view(), name='report_detail'),
    path('reports/<int:pk>/edit/', ReportUpdateView.as_view(), name='report_update'),
    path('reports/<int:pk>/delete/', ReportDeleteView.as_view(), name='report_delete'),
    path('reports/<int:pk>/generate/', generate_report, name='generate_report'),

    # Custom Reports
    path('custom-report/', generate_custom_report, name='generate_custom_report'),
]
