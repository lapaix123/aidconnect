from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import authenticate, login
from django.db.models import Count, Q
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import User, Beneficiary, Case, CaseNote, Assessment, AssessmentQuestion, AssessmentAnswer
from .serializers import (
    UserSerializer, BeneficiarySerializer, CaseSerializer, CaseNoteSerializer,
    AssessmentSerializer, AssessmentQuestionSerializer, AssessmentAnswerSerializer
)

# Authentication Views
def login_view(request):
    """Custom login view that serves the login page at the root URL"""
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard_redirect')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

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

# Custom Mixins
class RoleRequiredMixin(UserPassesTestMixin):
    """Mixin that checks if the user has the required role(s)"""
    allowed_roles = []

    def test_func(self):
        return self.request.user.role in self.allowed_roles

class AdminRequiredMixin(RoleRequiredMixin):
    """Mixin that checks if the user is an admin"""
    allowed_roles = ['admin']

class AdminOrCaseManagerRequiredMixin(RoleRequiredMixin):
    """Mixin that checks if the user is an admin or case manager"""
    allowed_roles = ['admin', 'case_manager']

class AnyRoleRequiredMixin(RoleRequiredMixin):
    """Mixin that allows any authenticated user with a valid role"""
    allowed_roles = ['admin', 'case_manager', 'field_officer']

# Beneficiary Views
class BeneficiaryListView(LoginRequiredMixin, AnyRoleRequiredMixin, ListView):
    model = Beneficiary
    template_name = 'beneficiaries/beneficiary_list.html'
    context_object_name = 'beneficiaries'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # Apply search filter
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(address__icontains=search_query)
            )

        # Apply gender filter
        gender = self.request.GET.get('gender', '')
        if gender:
            queryset = queryset.filter(gender=gender)

        # Apply sorting
        sort = self.request.GET.get('sort', 'name')
        queryset = queryset.order_by(sort)

        return queryset

# Case Views
class CaseListView(LoginRequiredMixin, AnyRoleRequiredMixin, ListView):
    model = Case
    template_name = 'cases/case_list.html'
    context_object_name = 'cases'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter cases based on user role
        if self.request.user.role == 'case_manager':
            queryset = queryset.filter(case_manager=self.request.user)
        elif self.request.user.role == 'field_officer':
            # Field officers can only see cases they've contributed to
            case_notes = CaseNote.objects.filter(created_by=self.request.user).values_list('case_id', flat=True)
            assessments = Assessment.objects.filter(created_by=self.request.user).values_list('case_id', flat=True)
            queryset = queryset.filter(Q(id__in=case_notes) | Q(id__in=assessments)).distinct()

        # Apply search filter
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(beneficiary__name__icontains=search_query)
            )

        # Apply status filter
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)

        # Apply sorting
        sort = self.request.GET.get('sort', '-created_at')
        queryset = queryset.order_by(sort)

        return queryset

class BeneficiaryDetailView(LoginRequiredMixin, AnyRoleRequiredMixin, DetailView):
    model = Beneficiary
    template_name = 'beneficiaries/beneficiary_detail.html'
    context_object_name = 'beneficiary'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        beneficiary = self.get_object()

        # Get related data
        context['cases'] = Case.objects.filter(beneficiary=beneficiary)
        context['active_cases'] = context['cases'].filter(status='open')

        # Get assessments from all cases
        case_ids = context['cases'].values_list('id', flat=True)
        context['assessments'] = Assessment.objects.filter(case__id__in=case_ids)

        # Get case notes from all cases
        context['case_notes'] = CaseNote.objects.filter(case__id__in=case_ids)

        return context

class CaseDetailView(LoginRequiredMixin, AnyRoleRequiredMixin, DetailView):
    model = Case
    template_name = 'cases/case_detail.html'
    context_object_name = 'case'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        case = self.get_object()

        # Get related data
        context['assessments'] = Assessment.objects.filter(case=case).order_by('-created_at')
        context['case_notes'] = CaseNote.objects.filter(case=case).order_by('-created_at')

        return context

class CaseCreateView(LoginRequiredMixin, AdminOrCaseManagerRequiredMixin, CreateView):
    model = Case
    template_name = 'cases/case_form.html'
    fields = ['title', 'beneficiary', 'status', 'description']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit beneficiary choices based on user role
        if self.request.user.role == 'case_manager':
            # Case managers can see all beneficiaries
            pass
        return form

    def form_valid(self, form):
        # Set the case manager to the current user if they are a case manager
        if self.request.user.role == 'case_manager':
            form.instance.case_manager = self.request.user
        messages.success(self.request, f"Case '{form.instance.title}' created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('case_detail', kwargs={'pk': self.object.pk})

class CaseUpdateView(LoginRequiredMixin, AdminOrCaseManagerRequiredMixin, UpdateView):
    model = Case
    template_name = 'cases/case_form.html'
    fields = ['title', 'beneficiary', 'status', 'description']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Case managers can only update their own cases
        if self.request.user.role == 'case_manager':
            queryset = queryset.filter(case_manager=self.request.user)
        return queryset

    def form_valid(self, form):
        messages.success(self.request, f"Case '{form.instance.title}' updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('case_detail', kwargs={'pk': self.object.pk})

class CaseDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Case
    template_name = 'cases/case_confirm_delete.html'
    context_object_name = 'case'
    success_url = reverse_lazy('case_list')

    def delete(self, request, *args, **kwargs):
        case = self.get_object()
        messages.success(request, f"Case '{case.title}' deleted successfully.")
        return super().delete(request, *args, **kwargs)

# Assessment Views
class AssessmentListView(LoginRequiredMixin, AnyRoleRequiredMixin, ListView):
    model = Assessment
    template_name = 'assessments/assessment_list.html'
    context_object_name = 'assessments'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter assessments based on user role
        if self.request.user.role == 'case_manager':
            # Case managers can see assessments for their cases
            case_ids = Case.objects.filter(case_manager=self.request.user).values_list('id', flat=True)
            queryset = queryset.filter(case__id__in=case_ids)
        elif self.request.user.role == 'field_officer':
            # Field officers can only see assessments they created
            queryset = queryset.filter(created_by=self.request.user)

        # Apply search filter
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(case__title__icontains=search_query) |
                Q(case__beneficiary__name__icontains=search_query)
            )

        # Apply sorting
        sort = self.request.GET.get('sort', '-created_at')
        queryset = queryset.order_by(sort)

        return queryset

class AssessmentDetailView(LoginRequiredMixin, AnyRoleRequiredMixin, DetailView):
    model = Assessment
    template_name = 'assessments/assessment_detail.html'
    context_object_name = 'assessment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assessment = self.get_object()

        # Get related data
        context['questions'] = AssessmentQuestion.objects.filter(assessment=assessment).order_by('order')
        context['answers'] = AssessmentAnswer.objects.filter(question__assessment=assessment)

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter based on user role
        if self.request.user.role == 'case_manager':
            # Case managers can see assessments for their cases
            case_ids = Case.objects.filter(case_manager=self.request.user).values_list('id', flat=True)
            queryset = queryset.filter(case__id__in=case_ids)
        elif self.request.user.role == 'field_officer':
            # Field officers can only see assessments they created
            queryset = queryset.filter(created_by=self.request.user)
        return queryset

class AssessmentCreateView(LoginRequiredMixin, AnyRoleRequiredMixin, CreateView):
    model = Assessment
    template_name = 'assessments/assessment_form.html'
    fields = ['title', 'case', 'description']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit case choices based on user role
        if self.request.user.role == 'case_manager':
            form.fields['case'].queryset = Case.objects.filter(case_manager=self.request.user)
        elif self.request.user.role == 'field_officer':
            # Field officers can see all cases to create assessments
            # This allows them to contribute to cases even if they haven't before
            form.fields['case'].queryset = Case.objects.all()
        return form

    def form_valid(self, form):
        # Set the creator to the current user
        form.instance.created_by = self.request.user
        messages.success(self.request, f"Assessment '{form.instance.title}' created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('assessment_detail', kwargs={'pk': self.object.pk})

class AssessmentUpdateView(LoginRequiredMixin, AdminOrCaseManagerRequiredMixin, UpdateView):
    model = Assessment
    template_name = 'assessments/assessment_form.html'
    fields = ['title', 'case', 'description']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Case managers can only update assessments for their cases
        if self.request.user.role == 'case_manager':
            case_ids = Case.objects.filter(case_manager=self.request.user).values_list('id', flat=True)
            queryset = queryset.filter(case__id__in=case_ids)
        return queryset

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit case choices based on user role
        if self.request.user.role == 'case_manager':
            form.fields['case'].queryset = Case.objects.filter(case_manager=self.request.user)
        return form

    def form_valid(self, form):
        messages.success(self.request, f"Assessment '{form.instance.title}' updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('assessment_detail', kwargs={'pk': self.object.pk})

class AssessmentDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Assessment
    template_name = 'assessments/assessment_confirm_delete.html'
    context_object_name = 'assessment'
    success_url = reverse_lazy('assessment_list')

    def delete(self, request, *args, **kwargs):
        assessment = self.get_object()
        messages.success(request, f"Assessment '{assessment.title}' deleted successfully.")
        return super().delete(request, *args, **kwargs)

# Case Note Views
class CaseNoteListView(LoginRequiredMixin, AnyRoleRequiredMixin, ListView):
    model = CaseNote
    template_name = 'case_notes/case_note_list.html'
    context_object_name = 'case_notes'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter case notes based on user role
        if self.request.user.role == 'case_manager':
            # Case managers can see notes for their cases
            case_ids = Case.objects.filter(case_manager=self.request.user).values_list('id', flat=True)
            queryset = queryset.filter(case__id__in=case_ids)
        elif self.request.user.role == 'field_officer':
            # Field officers can only see notes they created
            queryset = queryset.filter(created_by=self.request.user)

        # Apply search filter
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(content__icontains=search_query) | 
                Q(case__title__icontains=search_query) |
                Q(case__beneficiary__name__icontains=search_query)
            )

        # Apply sorting
        sort = self.request.GET.get('sort', '-created_at')
        queryset = queryset.order_by(sort)

        return queryset

class CaseNoteDetailView(LoginRequiredMixin, AnyRoleRequiredMixin, DetailView):
    model = CaseNote
    template_name = 'case_notes/case_note_detail.html'
    context_object_name = 'case_note'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter based on user role
        if self.request.user.role == 'case_manager':
            # Case managers can see notes for their cases
            case_ids = Case.objects.filter(case_manager=self.request.user).values_list('id', flat=True)
            queryset = queryset.filter(case__id__in=case_ids)
        elif self.request.user.role == 'field_officer':
            # Field officers can only see notes they created
            queryset = queryset.filter(created_by=self.request.user)
        return queryset

class CaseNoteCreateView(LoginRequiredMixin, AnyRoleRequiredMixin, CreateView):
    model = CaseNote
    template_name = 'case_notes/case_note_form.html'
    fields = ['case', 'content']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit case choices based on user role
        if self.request.user.role == 'case_manager':
            form.fields['case'].queryset = Case.objects.filter(case_manager=self.request.user)
        elif self.request.user.role == 'field_officer':
            # Field officers can see all cases to create notes
            # This allows them to contribute to cases even if they haven't before
            form.fields['case'].queryset = Case.objects.all()
        return form

    def form_valid(self, form):
        # Set the creator to the current user
        form.instance.created_by = self.request.user
        messages.success(self.request, "Case note created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('case_note_detail', kwargs={'pk': self.object.pk})

class CaseNoteUpdateView(LoginRequiredMixin, AnyRoleRequiredMixin, UpdateView):
    model = CaseNote
    template_name = 'case_notes/case_note_form.html'
    fields = ['case', 'content']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Users can only update their own notes
        queryset = queryset.filter(created_by=self.request.user)
        return queryset

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit case choices based on user role
        if self.request.user.role == 'case_manager':
            form.fields['case'].queryset = Case.objects.filter(case_manager=self.request.user)
        elif self.request.user.role == 'field_officer':
            # Field officers can see all cases when updating notes
            # This allows them to move their notes to different cases if needed
            form.fields['case'].queryset = Case.objects.all()
        return form

    def form_valid(self, form):
        messages.success(self.request, "Case note updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('case_note_detail', kwargs={'pk': self.object.pk})

class CaseNoteDeleteView(LoginRequiredMixin, AnyRoleRequiredMixin, DeleteView):
    model = CaseNote
    template_name = 'case_notes/case_note_confirm_delete.html'
    context_object_name = 'case_note'
    success_url = reverse_lazy('case_note_list')

    def get_queryset(self):
        queryset = super().get_queryset()
        # Users can only delete their own notes, admins can delete any
        if self.request.user.role != 'admin':
            queryset = queryset.filter(created_by=self.request.user)
        return queryset

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Case note deleted successfully.")
        return super().delete(request, *args, **kwargs)

# Visit Views (for Field Officers)
class VisitListView(CaseNoteListView):
    """Alias for CaseNoteListView with a different template for Field Officers"""
    template_name = 'visits/visit_list.html'

    def get_queryset(self):
        # Ensure only field officers can access this view
        if self.request.user.role != 'field_officer':
            return CaseNote.objects.none()
        return super().get_queryset()

class BeneficiaryCreateView(LoginRequiredMixin, AdminOrCaseManagerRequiredMixin, CreateView):
    model = Beneficiary
    template_name = 'beneficiaries/beneficiary_form.html'
    fields = ['name', 'gender', 'dob', 'address']

    def get_success_url(self):
        return reverse('beneficiary_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f"Beneficiary '{form.instance.name}' created successfully.")
        return super().form_valid(form)

class BeneficiaryUpdateView(LoginRequiredMixin, AdminOrCaseManagerRequiredMixin, UpdateView):
    model = Beneficiary
    template_name = 'beneficiaries/beneficiary_form.html'
    fields = ['name', 'gender', 'dob', 'address']

    def get_success_url(self):
        return reverse('beneficiary_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f"Beneficiary '{form.instance.name}' updated successfully.")
        return super().form_valid(form)

class BeneficiaryDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Beneficiary
    template_name = 'beneficiaries/beneficiary_confirm_delete.html'
    context_object_name = 'beneficiary'
    success_url = reverse_lazy('beneficiary_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        beneficiary = self.get_object()

        # Get related data
        context['cases'] = Case.objects.filter(beneficiary=beneficiary)

        # Get assessments from all cases
        case_ids = context['cases'].values_list('id', flat=True)
        context['assessments'] = Assessment.objects.filter(case__id__in=case_ids)

        # Get case notes from all cases
        context['case_notes'] = CaseNote.objects.filter(case__id__in=case_ids)

        return context

    def delete(self, request, *args, **kwargs):
        beneficiary = self.get_object()
        messages.success(request, f"Beneficiary '{beneficiary.name}' deleted successfully.")
        return super().delete(request, *args, **kwargs)

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
