# ===== lab_simulations/urls.py =====
from django.urls import path
from . import views

urlpatterns = [
    path('', views.SimulationListView.as_view(), name='simulation_list'),
    path('simulation/<int:pk>/', views.SimulationDetailView.as_view(), name='simulation_detail'),
    path('create/', views.SimulationCreateView.as_view(), name='simulation_create'),
    path('simulation/<int:pk>/edit/', views.SimulationUpdateView.as_view(), name='simulation_update'),
    path('simulation/<int:pk>/delete/', views.SimulationDeleteView.as_view(), name='simulation_delete'),
    path('simulation/<int:pk>/submit/', views.submit_quiz, name='submit_quiz'),
    path('simulation/<int:pk>/results/', views.quiz_results, name='quiz_results'),
    path('quiz_history/', views.QuizHistoryView.as_view(), name='quiz_history'), # NEW URL
]