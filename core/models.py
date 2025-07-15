from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """Custom user model with role field"""
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('case_manager', 'Case Manager'),
        ('field_officer', 'Field Officer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='field_officer')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Beneficiary(models.Model):
    """Beneficiary model with personal information"""
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    name = models.CharField(max_length=100)
    dob = models.DateField(verbose_name="Date of Birth")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    address = models.TextField()
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
