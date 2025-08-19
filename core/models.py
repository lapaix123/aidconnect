from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import json

class User(AbstractUser):
    """Custom user model with role field"""
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('case_manager', 'Case Manager'),
        ('field_officer', 'Field Officer'),
        ('partner_organisation', 'Partner Organisation'),
        ('monitoring_and_evaluation', 'Monitoring and Evaluation'),
        ('program_director', 'Program Director'),
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='field_officer')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
class Program(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount a beneficiary receives per month")
    next_program = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, help_text="Optional: Promote to this program after conditions are met")

    def __str__(self):
        return self.name
class BeneficiaryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    max_annual_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Maximum yearly amount a beneficiary in this category can receive")

    def __str__(self):
        return self.name

class Beneficiary(models.Model):
    name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    address = models.TextField()
    category = models.ForeignKey(BeneficiaryCategory, on_delete=models.SET_NULL, null=True, related_name='beneficiaries')
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True, related_name='beneficiaries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


    class Meta:
        verbose_name_plural = "Beneficiaries"

class Case(models.Model):
    """Case model linked to a beneficiary and case manager"""
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('pending', 'Pending'),
    )
    title = models.CharField(max_length=200)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='cases')
    case_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_cases')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    description = models.TextField(blank=True)
    opened_date = models.DateTimeField(default=timezone.now)
    closed_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.beneficiary.name}"

class CaseNote(models.Model):
    """Case note linked to a case and created by a user"""
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='notes')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='case_notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Note for {self.case.title} by {self.created_by.username}"

class Assessment(models.Model):
    """Assessment model for evaluating beneficiaries"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='assessments')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assessments')
    amount_received = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Amount received in this assessment")
    year = models.PositiveIntegerField(default=timezone.now().year)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class AssessmentQuestion(models.Model):
    """Question for assessments"""
    QUESTION_TYPES = (
        ('text', 'Text'),
        ('number', 'Number'),
        ('boolean', 'Yes/No'),
        ('choice', 'Multiple Choice'),
    )
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    choices = models.TextField(blank=True, help_text="Comma-separated choices for multiple choice questions")
    required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['order']

class AssessmentAnswer(models.Model):
    """Answer to an assessment question"""
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_answers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Answer to {self.question.text[:30]}..."


class ReportTemplate(models.Model):
    """Template for generating reports"""
    ENTITY_CHOICES = (
        ('beneficiary', 'Beneficiaries'),
        ('case', 'Cases'),
        ('assessment', 'Assessments'),
        ('case_note', 'Case Notes'),
        ('program', 'Programs'),
        ('category', 'Categories'),
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    entity_type = models.CharField(max_length=20, choices=ENTITY_CHOICES)
    fields = models.TextField(help_text="JSON array of field names to include in the report")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_fields_list(self):
        """Returns the list of fields from the JSON string"""
        try:
            return json.loads(self.fields)
        except:
            return []


class Report(models.Model):
    """Saved report configuration"""
    FORMAT_CHOICES = (
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
    )

    name = models.CharField(max_length=100)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='reports')
    filters = models.TextField(blank=True, help_text="JSON object of filters to apply")
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='excel')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_filters_dict(self):
        """Returns the filters as a dictionary from the JSON string"""
        try:
            return json.loads(self.filters)
        except:
            return {}


class Referral(models.Model):
    """Referral model for tracking referrals between organizations"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )

    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='referrals')
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='referrals', null=True, blank=True)
    referred_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referred_to_organization = models.CharField(max_length=100)
    referred_to_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals_received')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Referral for {self.beneficiary.name} to {self.referred_to_organization}"


class Alert(models.Model):
    """Alert model for system notifications and alerts"""
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )

    title = models.CharField(max_length=100)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    related_to = models.CharField(max_length=50, blank=True, help_text="Type of entity this alert is related to (e.g., case, beneficiary)")
    related_id = models.PositiveIntegerField(null=True, blank=True, help_text="ID of the related entity")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
