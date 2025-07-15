# AidConnect Data Models

This document provides detailed information about the data models used in the AidConnect system.

## User Model

The User model extends Django's built-in AbstractUser to add role-based access control.

```python
class User(AbstractUser):
    """Custom user model with role field"""
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('case_manager', 'Case Manager'),
        ('field_officer', 'Field Officer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='field_officer')
```

### Fields:
- All fields from Django's AbstractUser (username, email, password, etc.)
- **role**: CharField with choices 'admin', 'case_manager', or 'field_officer'

### Relationships:
- One-to-many with Case (as case_manager)
- One-to-many with CaseNote (as created_by)
- One-to-many with Assessment (as created_by)
- One-to-many with AssessmentAnswer (as created_by)

## Beneficiary Model

The Beneficiary model stores information about individuals receiving aid.

```python
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
```

### Fields:
- **name**: CharField, the beneficiary's full name
- **dob**: DateField, date of birth
- **gender**: CharField with choices 'male', 'female', or 'other'
- **address**: TextField for storing the beneficiary's address
- **created_at**: DateTimeField, automatically set when created
- **updated_at**: DateTimeField, automatically updated when modified

### Relationships:
- One-to-many with Case (a beneficiary can have multiple cases)

## Case Model

The Case model represents a specific intervention or service provided to a beneficiary.

```python
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
```

### Fields:
- **title**: CharField, the title or name of the case
- **beneficiary**: ForeignKey to Beneficiary
- **case_manager**: ForeignKey to User
- **status**: CharField with choices 'open', 'closed', or 'pending'
- **description**: TextField, optional description of the case
- **opened_date**: DateTimeField, when the case was opened
- **closed_date**: DateTimeField, when the case was closed (if applicable)
- **created_at**: DateTimeField, automatically set when created
- **updated_at**: DateTimeField, automatically updated when modified

### Relationships:
- Many-to-one with Beneficiary
- Many-to-one with User (as case_manager)
- One-to-many with CaseNote
- One-to-many with Assessment

## CaseNote Model

The CaseNote model stores notes and updates related to a specific case.

```python
class CaseNote(models.Model):
    """Case note linked to a case and created by a user"""
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='notes')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='case_notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Fields:
- **case**: ForeignKey to Case
- **created_by**: ForeignKey to User
- **content**: TextField, the content of the note
- **created_at**: DateTimeField, automatically set when created
- **updated_at**: DateTimeField, automatically updated when modified

### Relationships:
- Many-to-one with Case
- Many-to-one with User (as created_by)

## Assessment Model

The Assessment model represents a structured evaluation of a beneficiary's needs or situation.

```python
class Assessment(models.Model):
    """Assessment model for evaluating beneficiaries"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='assessments')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assessments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Fields:
- **title**: CharField, the title of the assessment
- **description**: TextField, optional description of the assessment
- **case**: ForeignKey to Case
- **created_by**: ForeignKey to User
- **created_at**: DateTimeField, automatically set when created
- **updated_at**: DateTimeField, automatically updated when modified

### Relationships:
- Many-to-one with Case
- Many-to-one with User (as created_by)
- One-to-many with AssessmentQuestion

## AssessmentQuestion Model

The AssessmentQuestion model defines questions to be answered in an assessment.

```python
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
```

### Fields:
- **assessment**: ForeignKey to Assessment
- **text**: TextField, the question text
- **question_type**: CharField with choices 'text', 'number', 'boolean', or 'choice'
- **choices**: TextField, comma-separated choices for multiple choice questions
- **required**: BooleanField, whether the question is required
- **order**: PositiveIntegerField, the order of the question in the assessment

### Relationships:
- Many-to-one with Assessment
- One-to-many with AssessmentAnswer

## AssessmentAnswer Model

The AssessmentAnswer model stores answers to assessment questions.

```python
class AssessmentAnswer(models.Model):
    """Answer to an assessment question"""
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_answers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Fields:
- **question**: ForeignKey to AssessmentQuestion
- **answer_text**: TextField, the answer to the question
- **created_by**: ForeignKey to User
- **created_at**: DateTimeField, automatically set when created
- **updated_at**: DateTimeField, automatically updated when modified

### Relationships:
- Many-to-one with AssessmentQuestion
- Many-to-one with User (as created_by)

## Entity Relationship Diagram

```
User
├── managed_cases (Case)
├── case_notes (CaseNote)
├── created_assessments (Assessment)
└── assessment_answers (AssessmentAnswer)

Beneficiary
└── cases (Case)

Case
├── beneficiary (Beneficiary)
├── case_manager (User)
├── notes (CaseNote)
└── assessments (Assessment)

CaseNote
├── case (Case)
└── created_by (User)

Assessment
├── case (Case)
├── created_by (User)
└── questions (AssessmentQuestion)

AssessmentQuestion
├── assessment (Assessment)
└── answers (AssessmentAnswer)

AssessmentAnswer
├── question (AssessmentQuestion)
└── created_by (User)
```