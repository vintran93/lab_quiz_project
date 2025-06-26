# ===== lab_simulations/models.py =====
from django.db import models
from django.urls import reverse

class LabSimulation(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='uploads/', help_text="Upload network topology image")
    task = models.TextField(help_text="Enter the task description")
    questions = models.TextField(help_text="Enter the questions (one per line or paragraph)")
    lab_answers = models.TextField(help_text="Enter the correct lab answers")
    user_answers = models.TextField(blank=True, help_text="User's submitted answers")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('simulation_detail', kwargs={'pk': self.pk})

    def calculate_score(self):
        """Calculate quiz score by comparing user answers with lab answers"""
        if not self.user_answers or not self.lab_answers:
            return 0
        
        # Simple scoring - you can enhance this logic
        lab_lines = [line.strip().lower() for line in self.lab_answers.split('\n') if line.strip()]
        user_lines = [line.strip().lower() for line in self.user_answers.split('\n') if line.strip()]
        
        if not lab_lines:
            return 0
        
        correct = 0
        total = len(lab_lines)
        
        for i, lab_answer in enumerate(lab_lines):
            if i < len(user_lines):
                # Simple text similarity check
                if lab_answer in user_lines[i] or user_lines[i] in lab_answer:
                    correct += 1
        
        return round((correct / total) * 100, 2)