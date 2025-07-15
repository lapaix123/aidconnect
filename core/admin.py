from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Beneficiary, Case, CaseNote, 
    Assessment, AssessmentQuestion, AssessmentAnswer
)

# Register your models here.
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'dob', 'created_at')
    list_filter = ('gender', 'created_at')
    search_fields = ('name', 'address')

class CaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'beneficiary', 'case_manager', 'status', 'opened_date')
    list_filter = ('status', 'opened_date', 'case_manager')
    search_fields = ('title', 'description', 'beneficiary__name')

class CaseNoteAdmin(admin.ModelAdmin):
    list_display = ('case', 'created_by', 'created_at')
    list_filter = ('created_at', 'created_by')
    search_fields = ('content', 'case__title')

class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'case', 'created_by', 'created_at')
    list_filter = ('created_at', 'created_by')
    search_fields = ('title', 'description', 'case__title')

class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'assessment', 'question_type', 'required', 'order')
    list_filter = ('question_type', 'required', 'assessment')
    search_fields = ('text', 'assessment__title')

class AssessmentAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_by', 'created_at')
    list_filter = ('created_at', 'created_by', 'question__question_type')
    search_fields = ('answer_text', 'question__text')

# Register models with custom admin classes
admin.site.register(User, CustomUserAdmin)
admin.site.register(Beneficiary, BeneficiaryAdmin)
admin.site.register(Case, CaseAdmin)
admin.site.register(CaseNote, CaseNoteAdmin)
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(AssessmentQuestion, AssessmentQuestionAdmin)
admin.site.register(AssessmentAnswer, AssessmentAnswerAdmin)
