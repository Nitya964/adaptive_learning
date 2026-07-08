from django.contrib import admin
from .models import Course, Module, Question, UserProgress, QuizAttempt, SkillGap


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "created_at", "get_module_count"]
    search_fields = ["title", "description"]
    list_filter = ["created_at"]

    def get_module_count(self, obj):
        return obj.modules.count()

    get_module_count.short_description = "Modules"


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "course",
        "difficulty_level",
        "order",
        "get_question_count",
        "estimated_minutes",
    ]
    list_filter = ["difficulty_level", "course"]
    search_fields = ["title", "description"]
    ordering = ["course", "difficulty_level", "order"]

    def get_question_count(self, obj):
        return obj.questions.count()

    get_question_count.short_description = "Questions"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        "question_text",
        "module",
        "question_type",
        "difficulty_score",
        "correct_answer",
        "order",
    ]
    list_filter = ["question_type", "module", "difficulty_score"]
    search_fields = ["question_text", "tags"]
    ordering = ["module", "order"]


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "module",
        "score",
        "completed",
        "current_level",
        "attempts",
        "time_spent_minutes",
        "last_accessed",
    ]
    list_filter = ["completed", "current_level", "module"]
    search_fields = ["user__username", "module__title"]
    readonly_fields = ["last_accessed"]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "module",
        "score_percentage",
        "correct_answers",
        "total_questions",
        "time_taken_minutes",
        "adaptive_level",
        "attempted_at",
    ]
    list_filter = ["adaptive_level", "module", "attempted_at"]
    search_fields = ["user__username", "module__title"]
    readonly_fields = ["attempted_at"]


@admin.register(SkillGap)
class SkillGapAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "skill_name",
        "module",
        "current_score",
        "is_resolved",
        "detected_at",
    ]
    list_filter = ["is_resolved", "module", "detected_at"]
    search_fields = ["user__username", "skill_name"]
    readonly_fields = ["detected_at"]
