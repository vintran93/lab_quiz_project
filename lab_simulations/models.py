# ===== lab_simulations/models.py =====
from django.db import models
from django.urls import reverse
import re
from difflib import SequenceMatcher
from collections import Counter

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

    def normalize_text(self, text):
        """Normalize text for better comparison"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common punctuation that doesn't affect meaning
        text = re.sub(r'[.,;:!?"\'-]', '', text)
        
        # Remove articles and common words that don't affect technical meaning
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = text.split()
        words = [word for word in words if word not in common_words]
        
        return ' '.join(words).strip()

    def extract_key_terms(self, text):
        """Extract key technical terms from text"""
        if not text:
            return set()
        
        # Look for IP addresses, commands, technical terms
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b'
        command_pattern = r'\b(?:show|config|interface|ip|route|vlan|switch|router|ping|traceroute|telnet|ssh)\b'
        technical_pattern = r'\b[a-zA-Z]+\d+(?:/\d+)*\b'  # Interface names like eth0, gi0/1
        
        terms = set()
        
        # Extract IP addresses
        terms.update(re.findall(ip_pattern, text.lower()))
        
        # Extract commands
        terms.update(re.findall(command_pattern, text.lower()))
        
        # Extract technical identifiers
        terms.update(re.findall(technical_pattern, text.lower()))
        
        # Extract other significant words (3+ characters)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        terms.update(words)
        
        return terms

    def calculate_similarity(self, text1, text2):
        """Calculate similarity between two text strings"""
        if not text1 or not text2:
            return 0.0
        
        # Normalize both texts
        norm_text1 = self.normalize_text(text1)
        norm_text2 = self.normalize_text(text2)
        
        # If texts are identical after normalization
        if norm_text1 == norm_text2:
            return 1.0
        
        # Calculate sequence similarity
        seq_similarity = SequenceMatcher(None, norm_text1, norm_text2).ratio()
        
        # Extract and compare key terms
        terms1 = self.extract_key_terms(text1)
        terms2 = self.extract_key_terms(text2)
        
        if not terms1 and not terms2:
            return seq_similarity
        
        if not terms1 or not terms2:
            term_similarity = 0.0
        else:
            # Calculate Jaccard similarity for key terms
            intersection = len(terms1.intersection(terms2))
            union = len(terms1.union(terms2))
            term_similarity = intersection / union if union > 0 else 0.0
        
        # Weighted combination of sequence and term similarity
        # Give more weight to term similarity for technical content
        combined_similarity = (0.3 * seq_similarity) + (0.7 * term_similarity)
        
        return combined_similarity

    def calculate_score(self):
        """Calculate quiz score by comparing user answers with lab answers using enhanced comparison"""
        if not self.user_answers or not self.lab_answers:
            return 0
        
        # Split answers into lines and clean them
        lab_lines = [line.strip() for line in self.lab_answers.split('\n') if line.strip()]
        user_lines = [line.strip() for line in self.user_answers.split('\n') if line.strip()]
        
        if not lab_lines:
            return 0
        
        total_score = 0
        total_questions = len(lab_lines)
        
        # Compare each lab answer with corresponding user answer
        for i, lab_answer in enumerate(lab_lines):
            question_score = 0
            
            if i < len(user_lines):
                user_answer = user_lines[i]
                
                # Calculate similarity for the corresponding answer
                similarity = self.calculate_similarity(lab_answer, user_answer)
                
                # Convert similarity to score (with threshold)
                if similarity >= 0.8:  # High similarity threshold
                    question_score = 1.0
                elif similarity >= 0.6:  # Medium similarity
                    question_score = 0.8
                elif similarity >= 0.4:  # Low similarity
                    question_score = 0.5
                elif similarity >= 0.2:  # Very low similarity
                    question_score = 0.2
                else:
                    question_score = 0
            
            # Also check if user answer appears anywhere in user_lines (for flexible ordering)
            if question_score < 0.8:  # Only if we haven't found a good match yet
                best_match_score = 0
                for user_line in user_lines:
                    match_similarity = self.calculate_similarity(lab_answer, user_line)
                    if match_similarity > best_match_score:
                        best_match_score = match_similarity
                
                # Use the better score
                if best_match_score > similarity:
                    if best_match_score >= 0.8:
                        question_score = 0.9  # Slightly lower for out-of-order answers
                    elif best_match_score >= 0.6:
                        question_score = 0.7
                    elif best_match_score >= 0.4:
                        question_score = 0.4
                    elif best_match_score >= 0.2:
                        question_score = 0.1
            
            total_score += question_score
        
        # Calculate final percentage
        final_score = (total_score / total_questions) * 100
        return round(final_score, 2)

    def get_detailed_comparison(self):
        """Get detailed comparison results for debugging/review"""
        if not self.user_answers or not self.lab_answers:
            return []
        
        lab_lines = [line.strip() for line in self.lab_answers.split('\n') if line.strip()]
        user_lines = [line.strip() for line in self.user_answers.split('\n') if line.strip()]
        
        comparisons = []
        
        for i, lab_answer in enumerate(lab_lines):
            user_answer = user_lines[i] if i < len(user_lines) else ""
            similarity = self.calculate_similarity(lab_answer, user_answer)
            
            comparisons.append({
                'question_number': i + 1,
                'lab_answer': lab_answer,
                'user_answer': user_answer,
                'similarity': round(similarity, 3),
                'normalized_lab': self.normalize_text(lab_answer),
                'normalized_user': self.normalize_text(user_answer),
                'lab_terms': self.extract_key_terms(lab_answer),
                'user_terms': self.extract_key_terms(user_answer),
            })
        
        return comparisons