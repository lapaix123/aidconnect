from rest_framework import serializers
from .models import User, Beneficiary, Case, CaseNote, Assessment, AssessmentQuestion, AssessmentAnswer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = '__all__'

class CaseNoteSerializer(serializers.ModelSerializer):
    created_by_username = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = CaseNote
        fields = ['id', 'case', 'created_by', 'created_by_username', 'content', 'created_at', 'updated_at']

class AssessmentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentQuestion
        fields = '__all__'

class AssessmentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentAnswer
        fields = '__all__'

class AssessmentSerializer(serializers.ModelSerializer):
    questions = AssessmentQuestionSerializer(many=True, read_only=True)
    created_by_username = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Assessment
        fields = ['id', 'title', 'description', 'case', 'created_by', 'created_by_username', 'questions', 'created_at', 'updated_at']

class CaseSerializer(serializers.ModelSerializer):
    beneficiary_name = serializers.ReadOnlyField(source='beneficiary.name')
    case_manager_name = serializers.ReadOnlyField(source='case_manager.username')
    notes = CaseNoteSerializer(many=True, read_only=True)
    assessments = AssessmentSerializer(many=True, read_only=True)

    class Meta:
        model = Case
        fields = ['id', 'title', 'beneficiary', 'beneficiary_name', 'case_manager', 'case_manager_name', 
                  'status', 'description', 'opened_date', 'closed_date', 'notes', 'assessments', 
                  'created_at', 'updated_at']