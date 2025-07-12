# ===== lab_simulations/forms.py =====
from django import forms
from .models import LabSimulation

class LabSimulationForm(forms.ModelForm):
    class Meta:
        model = LabSimulation
        fields = ['title', 'image', 'task', 'questions', 'lab_answers']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter simulation title'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'task': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe the task for the simulation...'}),
            'questions': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Enter quiz questions, one per line or paragraph...'}),
            'lab_answers': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Enter correct lab answers corresponding to questions...'}),
        }
        labels = {
            'title': 'Simulation Title',
            'image': 'Network Topology Image',
            'task': 'Lab Task Description',
            'questions': 'Quiz Questions',
            'lab_answers': 'Correct Lab Answers',
        }

class QuizForm(forms.ModelForm):
    class Meta:
        model = LabSimulation
        fields = ['user_answers']
        widgets = {
            'user_answers': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Type your answers here...'}),
        }
        labels = {
            'user_answers': 'Your Submitted Answers',
        }

    # Add this __init__ method to clear the user_answers field
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Check if an instance is provided. If so, clear its user_answers.
        # This ensures that when the form is rendered, the textarea is empty.
        if self.instance:
            self.initial['user_answers'] = ""