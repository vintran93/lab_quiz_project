# Create this file as: lab_simulations/migrations/0002_quizattempt.py
# (adjust the number based on your existing migrations)

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lab_simulations', '0001_initial'),  # Replace with your last migration
    ]

    operations = [
        migrations.CreateModel(
            name='QuizAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_answers', models.TextField(help_text="User's submitted answers for this attempt")),
                ('score', models.DecimalField(decimal_places=2, help_text='Score achieved (0-100)', max_digits=5)),
                ('attempted_at', models.DateTimeField(auto_now_add=True)),
                ('simulation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to='lab_simulations.labsimulation')),
            ],
            options={
                'ordering': ['-attempted_at'],
            },
        ),
    ]