from django.db import models
from django.urls import reverse
import re
from difflib import SequenceMatcher
import difflib
import html
import unicodedata

# Helper function to preprocess text input
def _clean_text_input(text):
    """
    Cleans and normalizes raw text input to ensure consistent whitespace and character encoding.
    """
    if not text:
        return ""
    
    text = str(text).lower()
    text = unicodedata.normalize('NFKC', text)
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t\f\v]+', ' ', text)
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines]
    text = '\n'.join(cleaned_lines)
    text = re.sub(r'[^\sa-z0-9\-_./]', '', text) 
    text = text.strip()
    return text

# Helper function for tokenizing text while preserving delimiters
def _tokenize_with_delimiters(text, command_equivalencies_keys):
    tokens = []
    cleaned_text = _clean_text_input(text)
    sorted_aliases = sorted(list(command_equivalencies_keys), key=len, reverse=True)
    alias_patterns = [re.escape(alias) for alias in sorted_aliases]
    token_pattern = '|'.join(alias_patterns + [r'\n', r'[ \t\f\v]+', r'[^\s\w\n]+', r'\w+'])
    regex = re.compile(f"({token_pattern})", re.IGNORECASE)
    for match in regex.finditer(cleaned_text):
        token = match.group(0)
        tokens.append(token)
    final_tokens = [t for t in tokens if t]
    return final_tokens


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

    _COMMAND_EQUIVALENCIES = {
        'copy running-config startup-config': 'wr',
        'copy running-config start-up-config': 'wr',
        'copy running start': 'wr',
        'write memory': 'wr',
        'write mem': 'wr',
        'wr': 'wr',

        'configure terminal': 'conf t',
        'config t': 'conf t',
        'conf t': 'conf t',

        'interface': 'int',
        'int': 'int',
        
        'enable': 'en',
        'en': 'en',
        
        'no shutdown': 'no shut',
        'no shut': 'no shut',

        'exit': 'exit',
        'end': 'end',
        
        'line': 'line', 
    }
    _SORTED_EQUIVALENCY_KEYS = sorted(_COMMAND_EQUIVALENCIES.keys(), key=len, reverse=True)

    def normalize_text(self, text):
        if not text:
            return ""
        text = _clean_text_input(text)
        for alias in self._SORTED_EQUIVALENCY_KEYS:
            canonical_form = self._COMMAND_EQUIVALENCIES[alias]
            text = re.sub(r'\b' + re.escape(alias) + r'\b', canonical_form, text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[.,;:!?"\'-]', '', text)
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = text.split()
        words = [word for word in words if word not in common_words]
        return ' '.join(words)

    def _normalize_text_for_highlighting(self, token):
        if not token:
            return ""
        canonical_form = self._get_canonical_form(token)
        return canonical_form

    def _get_canonical_form(self, token_or_phrase):
        token_or_phrase_cleaned = _clean_text_input(token_or_phrase)
        if token_or_phrase_cleaned in self._COMMAND_EQUIVALENCIES:
             return self._COMMAND_EQUIVALENCIES[token_or_phrase_cleaned]
        return token_or_phrase_cleaned

    def _is_synonym_for_highlighting(self, original_user_token_raw, lab_expected_original_token_raw):
        """
        Determines if the raw user token is a recognized alias for the lab's expected token,
        qualifying it for GREEN highlighting.
        """
        original_user_token_cleaned = _clean_text_input(original_user_token_raw)
        lab_expected_original_token_cleaned = _clean_text_input(lab_expected_original_token_raw)

        user_canonical = self._get_canonical_form(original_user_token_cleaned)
        lab_canonical = self._get_canonical_form(lab_expected_original_token_cleaned)

        # A token is a synonym if:
        # 1. Their canonical forms match, AND
        # 2. The user token is different from the lab token (i.e., user used an alias)
        if user_canonical == lab_canonical and original_user_token_cleaned != lab_expected_original_token_cleaned:
            return True
        return False

    def _tokens_are_equivalent(self, user_token_raw, lab_token_raw):
        """
        Determines if two tokens are equivalent (either exact match or synonyms).
        """
        user_cleaned = _clean_text_input(user_token_raw)
        lab_cleaned = _clean_text_input(lab_token_raw)
        
        user_canonical = self._get_canonical_form(user_cleaned)
        lab_canonical = self._get_canonical_form(lab_cleaned)
        
        return user_canonical == lab_canonical

    def extract_key_terms(self, text):
        if not text:
            return set()
        text = _clean_text_input(text)
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b'
        command_pattern = r'\b(?:show|config(?:ure)?|interface|ip|route|vlan|switch|router|ping|traceroute|telnet|ssh|line|console|vty|exit|end|do|copy|write|terminal|access-list|port-security|channel-group|mode|active|trunk|allowed|native)\b'
        technical_pattern = r'\b[a-zA-Z]+\d+(?:/\d+)*\b'
        terms = set()
        terms.update(re.findall(ip_pattern, text.lower()))
        terms.update(re.findall(command_pattern, text.lower()))
        terms.update(re.findall(technical_pattern, text.lower()))
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        terms.update(words)
        return terms

    def calculate_similarity(self, text1, text2):
        if not text1 or not text2:
            return 0.0
        norm_text1 = self.normalize_text(text1)
        norm_text2 = self.normalize_text(text2)
        if norm_text1 == norm_text2:
            return 1.0
        seq_similarity = SequenceMatcher(None, norm_text1, norm_text2).ratio()
        terms1 = self.extract_key_terms(text1)
        terms2 = self.extract_key_terms(text2)
        if not terms1 and not terms2:
            return seq_similarity
        if not terms1 or not terms2:
            term_similarity = 0.0
        else:
            intersection = len(terms1.intersection(terms2))
            union = len(terms1.union(terms2))
            term_similarity = intersection / union if union > 0 else 0.0
        combined_similarity = (0.3 * seq_similarity) + (0.7 * term_similarity)
        return combined_similarity

    def calculate_score(self):
        if not self.user_answers or not self.lab_answers:
            return 0
        lab_lines = [_clean_text_input(line) for line in self.lab_answers.split('\n') if _clean_text_input(line)]
        user_lines = [_clean_text_input(line) for line in self.user_answers.split('\n') if _clean_text_input(line)]
        if not lab_lines:
            return 0
        total_score = 0
        total_questions = len(lab_lines)
        matched_user_indices = set() 

        for i, lab_answer in enumerate(lab_lines):
            question_score = 0
            current_line_match_score = 0
            direct_match_idx = -1 

            if i < len(user_lines):
                user_answer = user_lines[i]
                current_line_match_score = self.calculate_similarity(lab_answer, user_answer)
                if current_line_match_score >= 0.8:
                    question_score = 1.0
                    matched_user_indices.add(i)
                    direct_match_idx = i
            
            if question_score < 1.0:
                best_overall_match_score = current_line_match_score
                best_overall_match_idx = direct_match_idx

                for j, user_line_candidate in enumerate(user_lines):
                    if j not in matched_user_indices or j == direct_match_idx: 
                        similarity_candidate = self.calculate_similarity(lab_answer, user_line_candidate)
                        if similarity_candidate > best_overall_match_score:
                            best_overall_match_score = similarity_candidate
                            best_overall_match_idx = j
                
                if best_overall_match_score >= 0.9:
                    question_score = 0.9 
                elif best_overall_match_score >= 0.8:
                    question_score = 0.8
                elif best_overall_match_score >= 0.6:
                    question_score = 0.6
                elif best_overall_match_score >= 0.4:
                    question_score = 0.3
                elif best_overall_match_score >= 0.2:
                    question_score = 0.1
                else:
                    question_score = 0

                if question_score >= 0.8 and best_overall_match_idx != -1:
                    matched_user_indices.add(best_overall_match_idx)

            total_score += question_score
        
        final_score = (total_score / total_questions) * 100
        return round(final_score, 2)

    def get_attempt_count(self):
        return self.attempts.count()

    def get_highlighted_user_answers_as_html(self):
        if not self.user_answers:
            return ""
        
        if not self.lab_answers:
            return html.escape(self.user_answers)

        user_tokens_raw = _tokenize_with_delimiters(self.user_answers, self._COMMAND_EQUIVALENCIES.keys()) 
        lab_tokens_raw = _tokenize_with_delimiters(self.lab_answers, self._COMMAND_EQUIVALENCIES.keys()) 

        highlighted_output = []
        
        # Process each user token
        for i, user_token in enumerate(user_tokens_raw):
            cleaned_user_token = _clean_text_input(user_token)
            
            # If it's not a word-like token (whitespace, punctuation), don't highlight
            if not cleaned_user_token or not re.search(r'\w', cleaned_user_token):
                highlighted_output.append(html.escape(user_token))
                continue
            
            # Check if there's a corresponding lab token at this position
            if i < len(lab_tokens_raw):
                lab_token = lab_tokens_raw[i]
                cleaned_lab_token = _clean_text_input(lab_token)
                
                # Check if the tokens are equivalent
                if self._tokens_are_equivalent(user_token, lab_token):
                    # They're equivalent - check if user typed a synonym
                    if self._is_synonym_for_highlighting(user_token, lab_token):
                        # User typed a synonym, highlight green
                        highlighted_output.append(f'<span class="correct-synonym-highlight">{html.escape(user_token)}</span>')
                    else:
                        # User typed the canonical form or exact match, don't highlight
                        highlighted_output.append(html.escape(user_token))
                else:
                    # Tokens are not equivalent, highlight red
                    highlighted_output.append(f'<span class="incorrect-highlight">{html.escape(user_token)}</span>')
            else:
                # No corresponding lab token (user has extra tokens), highlight red
                highlighted_output.append(f'<span class="incorrect-highlight">{html.escape(user_token)}</span>')
        
        return "".join(highlighted_output)


class QuizAttempt(models.Model):
    simulation = models.ForeignKey(LabSimulation, on_delete=models.CASCADE, related_name='attempts')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    attempt_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-attempt_date']

    def __str__(self):
        return f"{self.simulation.title} - {self.score}% on {self.attempt_date.strftime('%Y-%m-%d %H:%M')}"