# ===== lab_simulations/forms.py =====
from django import forms
from .models import LabSimulation

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

class QuizForm(forms.ModelForm):
    class Meta:
        model = LabSimulation
        fields = ['user_answers']
        widgets = {
            'user_answers': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Enter your answers here...'
            })
        }