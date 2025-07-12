# ===== lab_simulations/forms.py =====

from django import forms
# Ensure QuizAttempt is NOT imported here, as QuizSubmissionForm is not a ModelForm
from .models import LabSimulation # Only LabSimulation is needed for LabSimulationForm

class LabSimulationForm(forms.ModelForm):
    class Meta:
        model = LabSimulation
        fields = ['title', 'image', 'task', 'questions', 'lab_answers']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter simulation title'
            }),
            'task': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter the task description...'
            }),
            'questions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter questions (one per line or paragraph)...'
            }),
            'lab_answers': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter the correct lab answers...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

# THIS IS THE CORRECT FORM DEFINITION YOU PROVIDED EARLIER
class QuizSubmissionForm(forms.Form):
    user_answers = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Enter your answers here...'
        }),
        help_text='Enter your answers (one per line or paragraph)'
    )