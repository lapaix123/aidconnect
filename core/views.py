from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages
from django.urls import reverse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import User, Beneficiary, Case, CaseNote, Assessment, AssessmentQuestion, AssessmentAnswer
from .serializers import (
    UserSerializer, BeneficiarySerializer, CaseSerializer, CaseNoteSerializer,
    AssessmentSerializer, AssessmentQuestionSerializer, AssessmentAnswerSerializer
)

# API ViewSets
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class BeneficiaryViewSet(viewsets.ModelViewSet):
    queryset = Beneficiary.objects.all()
    serializer_class = BeneficiarySerializer
    permission_classes = [IsAuthenticated]

class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated]

class CaseNoteViewSet(viewsets.ModelViewSet):
    queryset = CaseNote.objects.all()
    serializer_class = CaseNoteSerializer
    permission_classes = [IsAuthenticated]

class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]

class AssessmentQuestionViewSet(viewsets.ModelViewSet):
    queryset = AssessmentQuestion.objects.all()
    serializer_class = AssessmentQuestionSerializer
    permission_classes = [IsAuthenticated]

class AssessmentAnswerViewSet(viewsets.ModelViewSet):
    queryset = AssessmentAnswer.objects.all()
    serializer_class = AssessmentAnswerSerializer
    permission_classes = [IsAuthenticated]

# Dashboard Views
@login_required
def dashboard_redirect(request):
    """Redirects users to the appropriate dashboard based on their role"""
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    elif request.user.role == 'case_manager':
        return redirect('case_manager_dashboard')
    elif request.user.role == 'field_officer':
        return redirect('field_officer_dashboard')
    else:
        messages.error(request, "Your account doesn't have a valid role assigned.")
        return redirect('login')

@login_required
def admin_dashboard(request):
    """Admin dashboard view"""
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('dashboard_redirect')

    # Get counts for dashboard cards
    user_count = User.objects.count()
    beneficiary_count = Beneficiary.objects.count()
    active_case_count = Case.objects.filter(status='open').count()
    assessment_count = Assessment.objects.count()

    # Get recent cases
    recent_cases = Case.objects.all().order_by('-created_at')[:10]

    context = {
        'user_count': user_count,
        'beneficiary_count': beneficiary_count,
        'active_case_count': active_case_count,
        'assessment_count': assessment_count,
        'recent_cases': recent_cases,
    }

    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def case_manager_dashboard(request):
    """Case manager dashboard view"""
    if request.user.role != 'case_manager':
        messages.error(request, "You don't have permission to access the case manager dashboard.")
        return redirect('dashboard_redirect')

    # Get counts for dashboard cards
    active_case_count = Case.objects.filter(case_manager=request.user, status='open').count()
    beneficiary_count = Beneficiary.objects.count()
    assessment_count = Assessment.objects.filter(created_by=request.user).count()

    # Get cases assigned to this case manager
    my_cases = Case.objects.filter(case_manager=request.user).order_by('-created_at')[:10]

    # Get recent case notes by this user
    recent_notes = CaseNote.objects.filter(created_by=request.user).order_by('-created_at')[:10]

    context = {
        'active_case_count': active_case_count,
        'beneficiary_count': beneficiary_count,
        'assessment_count': assessment_count,
        'my_cases': my_cases,
        'recent_notes': recent_notes,
    }

    return render(request, 'dashboard/case_manager_dashboard.html', context)

@login_required
def field_officer_dashboard(request):
    """Field officer dashboard view"""
    if request.user.role != 'field_officer':
        messages.error(request, "You don't have permission to access the field officer dashboard.")
        return redirect('dashboard_redirect')

    # Get counts for dashboard cards
    assessment_count = Assessment.objects.filter(created_by=request.user).count()
    case_note_count = CaseNote.objects.filter(created_by=request.user).count()
    beneficiary_count = Beneficiary.objects.count()

    # Get recent assessments by this user
    recent_assessments = Assessment.objects.filter(created_by=request.user).order_by('-created_at')[:10]

    # Get recent case notes by this user
    recent_notes = CaseNote.objects.filter(created_by=request.user).order_by('-created_at')[:10]

    context = {
        'assessment_count': assessment_count,
        'case_note_count': case_note_count,
        'beneficiary_count': beneficiary_count,
        'recent_assessments': recent_assessments,
        'recent_notes': recent_notes,
    }

    return render(request, 'dashboard/field_officer_dashboard.html', context)
