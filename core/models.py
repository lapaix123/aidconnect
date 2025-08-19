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
    income_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Beneficiary's annual income amount")
    year = models.PositiveIntegerField(default=timezone.now().year)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_total_amount_received(self):
        """
        Calculate the total amount received by the beneficiary across all assessments.
        Returns the total amount as a decimal.
        """
        beneficiary = self.case.beneficiary
        # Get all cases for this beneficiary
        case_ids = Case.objects.filter(beneficiary=beneficiary).values_list('id', flat=True)
        # Get all assessments for these cases
        assessments = Assessment.objects.filter(case__id__in=case_ids)
        # Sum the amount_received field
        total_amount = sum(assessment.amount_received for assessment in assessments)
        return total_amount

    def check_category_promotion(self):
        """
        Check if the beneficiary can be promoted to another category based on their income
        and total amount received.
        Returns a tuple (can_promote, new_category) where:
        - can_promote is a boolean indicating if the beneficiary can be promoted
        - new_category is the new category the beneficiary can be promoted to, or None if they can't be promoted
        """
        beneficiary = self.case.beneficiary
        current_category = beneficiary.category

        # Calculate total amount received by the beneficiary
        total_amount_received = self.get_total_amount_received()

        if not current_category:
            # If the beneficiary doesn't have a category, find an appropriate one based on income
            categories = BeneficiaryCategory.objects.filter(max_annual_amount__gte=self.income_amount).order_by('max_annual_amount')
            if categories.exists():
                return True, categories.first()
            return False, None

        # Check if the beneficiary's income is below the max annual amount for their current category
        # and if the total amount received is below the max annual amount
        if self.income_amount <= current_category.max_annual_amount and total_amount_received <= current_category.max_annual_amount:
            return False, None

        # Find categories with higher max annual amounts that can accommodate both income and total amount received
        higher_categories = BeneficiaryCategory.objects.filter(
            max_annual_amount__gt=current_category.max_annual_amount,
            max_annual_amount__gte=max(self.income_amount, total_amount_received)
        ).order_by('max_annual_amount')

        if higher_categories.exists():
            return True, higher_categories.first()

        return False, None

    def check_program_promotion(self):
        """
        Check if the beneficiary can be promoted to another program based on their current program.
        Returns a tuple (can_promote, new_program) where:
        - can_promote is a boolean indicating if the beneficiary can be promoted
        - new_program is the new program the beneficiary can be promoted to, or None if they can't be promoted
        """
        beneficiary = self.case.beneficiary
        current_program = beneficiary.program

        if not current_program:
            # If the beneficiary doesn't have a program, they can't be promoted
            return False, None

        # Check if the current program has a next program defined
        if current_program.next_program:
            return True, current_program.next_program

        return False, None


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


class ActionPlan(models.Model):
    """Action plan model for case managers to create plans for beneficiaries"""
    title = models.CharField(max_length=100)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='action_plans')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_action_plans')
    description = models.TextField(help_text="Detailed description of the action plan")
    goals = models.TextField(help_text="Goals to be achieved through this action plan")
    timeline = models.TextField(help_text="Timeline for completing the action plan")
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} for {self.case.beneficiary.name}"

    class Meta:
        ordering = ['-created_at']


class BeneficiaryProgress(models.Model):
    """Model for tracking beneficiary progress"""
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='progress_records')
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='progress_records', null=True, blank=True)
    action_plan = models.ForeignKey(ActionPlan, on_delete=models.SET_NULL, related_name='progress_records', null=True, blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recorded_progress')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ('on_track', 'On Track'),
        ('behind', 'Behind Schedule'),
        ('ahead', 'Ahead of Schedule'),
        ('completed', 'Completed'),
        ('not_started', 'Not Started')
    ], default='not_started')
    progress_percentage = models.PositiveIntegerField(default=0, help_text="Percentage of completion (0-100)")
    notes = models.TextField(blank=True, help_text="Notes about the progress")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Progress for {self.beneficiary.name} - {self.date}"

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Beneficiary Progress Records"
