# ===== lab_simulations/views.py =====
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import LabSimulation, QuizAttempt # Import QuizAttempt
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
            # Save the user's answers to the LabSimulation instance
            form.save()
            
            # Calculate the score
            score = simulation.calculate_score()
            
            # Create a new QuizAttempt record
            QuizAttempt.objects.create(
                simulation=simulation,
                score=score,
                # If you have user authentication, uncomment the line below
                # user=request.user 
            )
            
            messages.success(request, 'Quiz submitted successfully! Your score has been recorded.')
            return redirect('quiz_results', pk=simulation.pk)
    
    messages.error(request, 'Failed to submit quiz. Please try again.')
    return redirect('simulation_detail', pk=pk)

def quiz_results(request, pk):
    simulation = get_object_or_404(LabSimulation, pk=pk)
    score = simulation.calculate_score()
    
    context = {
        'simulation': simulation,
        'score': score,
    }
    return render(request, 'lab_simulations/quiz_results.html', context)

# NEW VIEW: To display quiz attempt history
class QuizHistoryView(ListView):
    model = QuizAttempt
    template_name = 'lab_simulations/quiz_history.html'
    context_object_name = 'quiz_attempts'
    paginate_by = 10 # Optional: paginate history if it gets long

    def get_queryset(self):
        # You might want to filter by user if you implement user authentication
        # return QuizAttempt.objects.filter(user=self.request.user).order_by('-attempt_date')
        return QuizAttempt.objects.all().order_by('-attempt_date')