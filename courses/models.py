from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class Course(models.Model):
    """Course containing multiple modules"""

    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image_url = models.URLField(
        blank=True, null=True, help_text="Optional course image"
    )

    def __str__(self):
        return self.title

    def get_modules_ordered(self):
        """Return modules ordered by difficulty and sequence"""
        return self.modules.all().order_by("difficulty_level", "order")


class Module(models.Model):
    """Module with difficulty levels (Beginner, Intermediate, Advanced)"""

    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty_level = models.CharField(
        max_length=20, choices=DIFFICULTY_CHOICES, default="beginner"
    )
    order = models.IntegerField(default=0, help_text="Sequence within difficulty level")
    prerequisite_module = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dependent_modules",
        help_text="Module that must be completed first",
    )
    estimated_minutes = models.IntegerField(
        default=30, help_text="Estimated time to complete"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["difficulty_level", "order"]

    def __str__(self):
        return f"{self.get_difficulty_level_display()}: {self.title}"

    def is_locked_for_user(self, user):
        """Check if module is locked based on prerequisite completion"""
        if not self.prerequisite_module:
            return False
        return not UserProgress.objects.filter(
            user=user, module=self.prerequisite_module, completed=True
        ).exists()


class Question(models.Model):
    """Quiz question with multiple choice answers"""

    QUESTION_TYPE_CHOICES = [
        ("mcq", "Multiple Choice"),
        ("true_false", "True/False"),
    ]

    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name="questions"
    )
    question_text = models.TextField()
    question_type = models.CharField(
        max_length=20, choices=QUESTION_TYPE_CHOICES, default="mcq"
    )
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500, blank=True, null=True)
    option_d = models.CharField(max_length=500, blank=True, null=True)
    correct_answer = models.CharField(max_length=1, help_text="A, B, C, or D")
    difficulty_score = models.IntegerField(
        default=50, help_text="1-100, higher = harder"
    )
    explanation = models.TextField(
        blank=True, help_text="Explanation shown after answering"
    )
    tags = models.CharField(
        max_length=200, blank=True, help_text="Comma-separated skill tags"
    )
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.question_text[:50] + "..."

    def check_answer(self, user_answer):
        """Check if user's answer is correct"""
        return user_answer.upper() == self.correct_answer.upper()

    def get_tags_list(self):
        """Return tags as a list"""
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]


class UserProgress(models.Model):
    """Track user progress through modules"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    current_level = models.CharField(
        max_length=20, choices=Module.DIFFICULTY_CHOICES, default="beginner"
    )
    last_accessed = models.DateTimeField(auto_now=True)
    score = models.IntegerField(default=0, help_text="Best score achieved (0-100)")
    attempts = models.IntegerField(default=0, help_text="Number of quiz attempts")
    time_spent_minutes = models.IntegerField(
        default=0, help_text="Total time spent on this module"
    )

    class Meta:
        unique_together = ["user", "module"]
        verbose_name_plural = "User Progress"

    def __str__(self):
        return f"{self.user.username} - {self.module.title} - {self.score}%"

    def update_progress(self, score, time_minutes):
        """Update progress after quiz attempt"""
        self.attempts += 1
        self.time_spent_minutes += time_minutes
        self.score = max(self.score, score)
        if score >= 70:  # Pass threshold
            self.completed = True
        self.last_accessed = timezone.now()
        self.save()


class QuizAttempt(models.Model):
    """Record of a quiz attempt with detailed answers"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="quiz_attempts"
    )
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name="quiz_attempts"
    )
    attempted_at = models.DateTimeField(auto_now_add=True)
    total_questions = models.IntegerField()
    correct_answers = models.IntegerField()
    score_percentage = models.FloatField()
    time_taken_minutes = models.IntegerField()
    answers_json = models.TextField(
        help_text="JSON storing question_id, user_answer, is_correct"
    )
    adaptive_level = models.CharField(max_length=20, choices=Module.DIFFICULTY_CHOICES)

    class Meta:
        ordering = ["-attempted_at"]
        verbose_name_plural = "Quiz Attempts"

    def __str__(self):
        return f"{self.user.username} - {self.module.title} - {self.score_percentage}%"

    def get_answers(self):
        """Parse and return answers as Python dict"""
        if not self.answers_json or self.answers_json.strip() == "":
            return []
        try:
            return json.loads(self.answers_json)
        except json.JSONDecodeError:
            return []

    def save_answers(self, answers_dict):
        """Save answers as JSON string"""
        self.answers_json = json.dumps(answers_dict)
        self.save()


class SkillGap(models.Model):
    """Track identified skill gaps for personalized remediation"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="skill_gaps")
    skill_name = models.CharField(max_length=100)
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name="skill_gaps"
    )
    detected_at = models.DateTimeField(auto_now_add=True)
    current_score = models.FloatField(help_text="Score in this skill (0-100)")
    recommended_action = models.TextField(
        help_text="Recommended learning path or practice"
    )
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-detected_at"]
        verbose_name_plural = "Skill Gaps"

    def __str__(self):
        return f"{self.user.username} - {self.skill_name} ({self.current_score}%)"

    @classmethod
    def detect_gaps(cls, user, module, quiz_attempt):
        """Detect skill gaps based on quiz performance"""
        gaps = []
        answers = quiz_attempt.get_answers()

        # Group answers by skill tags
        skill_performance = {}
        for answer in answers:
            question = Question.objects.get(id=answer["question_id"])
            tags = question.get_tags_list()

            for tag in tags:
                if tag not in skill_performance:
                    skill_performance[tag] = {"correct": 0, "total": 0}
                skill_performance[tag]["total"] += 1
                if answer["is_correct"]:
                    skill_performance[tag]["correct"] += 1

        # Create skill gaps for skills with < 50% accuracy
        for skill, stats in skill_performance.items():
            accuracy = (stats["correct"] / stats["total"]) * 100
            if accuracy < 50:
                gap, created = cls.objects.get_or_create(
                    user=user,
                    skill_name=skill,
                    module=module,
                    is_resolved=False,
                    defaults={
                        "current_score": accuracy,
                        "recommended_action": f"Review {skill} concepts in {module.title}. Practice similar questions to improve understanding.",
                    },
                )
                if not created:
                    gap.current_score = accuracy
                    gap.save()
                gaps.append(gap)

        return gaps
