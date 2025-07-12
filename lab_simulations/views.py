# ===== lab_simulations/views.py =====
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import LabSimulation, QuizAttempt
from .forms import LabSimulationForm, QuizForm


class SimulationListView(ListView):
    model = LabSimulation
    template_name = 'lab_simulations/simulation_list.html'
    context_object_name = 'simulations'
    paginate_by = 10

class SimulationDetailView(DetailView):
    model = LabSimulation
    template_name = 'lab_simulations/simulation_detail.html'
    context_object_name = 'simulation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz_form'] = QuizForm(instance=self.object)
        return context

class SimulationCreateView(CreateView):
    model = LabSimulation
    form_class = LabSimulationForm
    template_name = 'lab_simulations/simulation_form.html'
    success_url = reverse_lazy('simulation_list')

    def form_valid(self, form):
        messages.success(self.request, 'Lab simulation created successfully!')
        return super().form_valid(form)

class SimulationUpdateView(UpdateView):
    model = LabSimulation
    form_class = LabSimulationForm
    template_name = 'lab_simulations/simulation_form.html'
    success_url = reverse_lazy('simulation_list')

    def form_valid(self, form):
        messages.success(self.request, 'Lab simulation updated successfully!')
        return super().form_valid(form)

class SimulationDeleteView(DeleteView):
    model = LabSimulation
    template_name = 'lab_simulations/simulation_delete.html'
    success_url = reverse_lazy('simulation_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Lab simulation deleted successfully!')
        return super().delete(request, *args, **kwargs)

def submit_quiz(request, pk):
    simulation = get_object_or_404(LabSimulation, pk=pk)
    
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=simulation)
        if form.is_valid():
            form.save()
            
            score = simulation.calculate_score()
            
            QuizAttempt.objects.create(
                simulation=simulation,
                score=score,
            )
            
            messages.success(request, 'Quiz submitted successfully! Your score has been recorded.')
            return redirect('quiz_results', pk=simulation.pk)
    
    messages.error(request, 'Failed to submit quiz. Please try again.')
    return redirect('simulation_detail', pk=pk)

def quiz_results(request, pk):
    simulation = get_object_or_404(LabSimulation, pk=pk)
    score = simulation.calculate_score()
    
    # NEW: Get the HTML with highlighted user answers
    highlighted_user_answers_html = simulation.get_highlighted_user_answers_as_html()

    context = {
        'simulation': simulation,
        'score': score,
        'highlighted_user_answers_html': highlighted_user_answers_html, # Pass this to the template
    }
    return render(request, 'lab_simulations/quiz_results.html', context)

class QuizHistoryView(ListView):
    model = QuizAttempt
    template_name = 'lab_simulations/quiz_history.html'
    context_object_name = 'quiz_attempts'
    paginate_by = 10 

    def get_queryset(self):
        return QuizAttempt.objects.all().order_by('-attempt_date')

def clear_quiz_history(request, pk):
    simulation = get_object_or_404(LabSimulation, pk=pk)
    
    if request.method == 'POST':
        count, _ = simulation.attempts.all().delete()
        messages.success(request, f'{count} quiz attempts for "{simulation.title}" cleared successfully.')
        return redirect('quiz_history')
    
    context = {
        'simulation': simulation,
    }
    return render(request, 'lab_simulations/clear_history_confirm.html', context)

def delete_quiz_attempt(request, attempt_id):
    if request.method == 'POST':
        try:
            # For debugging - let's see what's happening
            print(f"User authenticated: {request.user.is_authenticated}")
            print(f"User: {request.user}")
            print(f"Attempt ID: {attempt_id}")
            
            # Get the quiz attempt - temporarily remove user check
            attempt = get_object_or_404(QuizAttempt, pk=attempt_id)
            quiz_title = attempt.simulation.title
            attempt.delete()
            
            # Single success message
            messages.success(request, f'Quiz attempt for "{quiz_title}" deleted successfully.')
            
        except Exception as e:
            messages.error(request, f'Error deleting quiz attempt: {str(e)}')
            print(f"Error: {e}")
    
    return redirect('quiz_history')