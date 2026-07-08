"""
Adaptive Learning Engine - AI Core for Personalized Learning Paths

This module implements:
1. Performance Analysis with Sigmoid-based level progression
2. Skill Gap Detection
3. Learning Path Generation
4. Velocity Calculation (Learning Speed)
"""

from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import UserProgress, QuizAttempt, Question, Module, SkillGap
import math


def sigmoid_function(x, center=50, scale=15):
    """
    Sigmoid function for smooth level progression.
    Returns value between 0-100 based on performance.

    Args:
        x: Input score (0-100)
        center: Midpoint where progression accelerates (default: 50)
        scale: Steepness of curve (default: 15)

    Returns:
        Adjusted level (0-100)
    """
    try:
        return 100 / (1 + math.exp(-(x - center) / scale))
    except (OverflowError, ValueError):
        return 0 if x < center else 100


def calculate_velocity(user, module, score, time_taken_minutes):
    """
    Calculate Learning Velocity: Accuracy per Minute

    Formula: (Score / 100) / Time in minutes
    Higher = Faster learning speed

    Args:
        user: User object
        module: Module object
        score: Quiz score (0-100)
        time_taken_minutes: Time taken for quiz

    Returns:
        Velocity score (float)
    """
    if time_taken_minutes <= 0:
        return 0.0

    accuracy = score / 100.0
    velocity = accuracy / time_taken_minutes

    # Normalize to more readable scale (multiply by 10)
    return round(velocity * 10, 3)


def analyze_performance(user, module, quiz_score, time_taken_minutes, quiz_attempt):
    """
    Core AI Analysis Function

    Analyzes user performance and updates learning path.

    Args:
        user: User object
        module: Module attempted
        quiz_score: Score achieved (0-100)
        time_taken_minutes: Time taken
        quiz_attempt: QuizAttempt object

    Returns:
        Dictionary with:
            - current_level: Updated level (0-100)
            - skill_gaps: List of detected skill gaps
            - next_module: Recommended next module
            - velocity: Learning speed score
            - performance_rating: 'excellent', 'good', 'needs_improvement'
            - adaptive_action: Suggested action
    """
    # 1. Calculate Velocity
    velocity = calculate_velocity(user, module, quiz_score, time_taken_minutes)

    # 2. Get or update UserProgress
    progress, created = UserProgress.objects.get_or_create(
        user=user,
        module=module,
        defaults={"current_level": "beginner", "score": quiz_score},
    )

    # Update progress
    progress.update_progress(quiz_score, time_taken_minutes)

    # 3. Calculate adaptive level using sigmoid function
    # Base level on quiz score with smooth progression
    new_level_value = sigmoid_function(quiz_score, center=60, scale=12)

    # Determine difficulty level based on sigmoid output
    if new_level_value < 40:
        current_level = "beginner"
    elif new_level_value < 70:
        current_level = "intermediate"
    else:
        current_level = "advanced"

    progress.current_level = current_level
    progress.save()

    # 4. Detect Skill Gaps
    skill_gaps = SkillGap.detect_gaps(user, module, quiz_attempt)

    # 5. Determine Performance Rating
    if quiz_score >= 85:
        performance_rating = "excellent"
        adaptive_action = "ready_to_advance"
    elif quiz_score >= 70:
        performance_rating = "good"
        adaptive_action = "consolidate_learning"
    elif quiz_score >= 50:
        performance_rating = "needs_practice"
        adaptive_action = "review_recommended"
    else:
        performance_rating = "needs_improvement"
        adaptive_action = "remediation_required"

    # 6. Generate Next Module Recommendation
    next_module = recommend_next_module(
        user, module, current_level, quiz_score, skill_gaps
    )

    return {
        "current_level": current_level,
        "level_value": round(new_level_value, 2),
        "skill_gaps": skill_gaps,
        "next_module": next_module,
        "velocity": velocity,
        "performance_rating": performance_rating,
        "adaptive_action": adaptive_action,
        "time_taken_minutes": time_taken_minutes,
        "quiz_score": quiz_score,
    }


def recommend_next_module(user, current_module, current_level, quiz_score, skill_gaps):
    """
    AI-Powered Learning Path Generation

    Recommends the next module based on:
    1. Current performance level
    2. Detected skill gaps
    3. Prerequisites completion
    4. Course structure

    Args:
        user: User object
        current_module: Module just completed
        current_level: User's current difficulty level
        quiz_score: Score achieved
        skill_gaps: List of SkillGap objects

    Returns:
        Recommended Module object or None
    """
    course = current_module.course

    # PRIORITY 1: If skill gaps detected, recommend remediation module
    if skill_gaps and quiz_score < 70:
        # Find a module that addresses the skill gaps
        # Look for modules with similar topic tags
        gap_topics = [gap.skill_name.lower() for gap in skill_gaps]

        # Search in same course for modules with matching tags
        for module in course.get_modules_ordered():
            if module != current_module:
                # Check if module tags match gap topics
                module_questions = module.questions.all()
                for question in module_questions:
                    question_tags = [tag.lower() for tag in question.get_tags_list()]
                    if any(topic in question_tags for topic in gap_topics):
                        if not module.is_locked_for_user(user):
                            return module

    # PRIORITY 2: If excellent performance (>85%), recommend harder module
    if quiz_score >= 85:
        # Find next module in same or higher difficulty
        current_order = current_module.order
        difficulty_order = ["beginner", "intermediate", "advanced"]
        current_difficulty_idx = difficulty_order.index(current_module.difficulty_level)

        # Try same difficulty, higher order
        next_in_level = (
            course.modules.filter(
                difficulty_level=current_module.difficulty_level,
                order__gt=current_order,
            )
            .order_by("order")
            .first()
        )

        if next_in_level and not next_in_level.is_locked_for_user(user):
            return next_in_level

        # Try next difficulty level
        if current_difficulty_idx < len(difficulty_order) - 1:
            next_difficulty = difficulty_order[current_difficulty_idx + 1]
            next_level_module = (
                course.modules.filter(difficulty_level=next_difficulty)
                .order_by("order")
                .first()
            )

            if next_level_module and not next_level_module.is_locked_for_user(user):
                return next_level_module

    # PRIORITY 3: Good performance (70-84%), consolidate with similar difficulty
    elif quiz_score >= 70:
        next_in_level = (
            course.modules.filter(
                difficulty_level=current_module.difficulty_level,
                order__gt=current_module.order,
            )
            .order_by("order")
            .first()
        )

        if next_in_level and not next_in_level.is_locked_for_user(user):
            return next_in_level

    # PRIORITY 4: Low performance, retry or find easier module
    else:
        # Check if there's a previous module to review
        previous_in_level = (
            course.modules.filter(
                difficulty_level=current_module.difficulty_level,
                order__lt=current_module.order,
            )
            .order_by("-order")
            .first()
        )

        if previous_in_level and not previous_in_level.is_locked_for_user(user):
            return previous_in_level

    # DEFAULT: Next unlocked module in course
    unlocked_modules = [
        m
        for m in course.get_modules_ordered()
        if not m.is_locked_for_user(user) and m != current_module
    ]

    if unlocked_modules:
        return unlocked_modules[0]

    return None


def get_user_knowledge_map(user):
    """
    Generate user's knowledge map across all modules

    Returns:
        Dictionary with:
            - completed_modules: List of completed modules
            - current_modules: List of in-progress modules
            - locked_modules: List of locked modules
            - overall_progress: Percentage (0-100)
    """
    all_progress = UserProgress.objects.filter(user=user).select_related("module")

    completed = [p.module for p in all_progress if p.completed]
    in_progress = [p.module for p in all_progress if not p.completed]

    # Get all courses the user has access to
    from .models import Course

    all_courses = Course.objects.all()
    all_modules = []
    locked = []

    for course in all_courses:
        for module in course.get_modules_ordered():
            if module not in completed and module not in in_progress:
                if not module.is_locked_for_user(user):
                    all_modules.append(module)
                else:
                    locked.append(module)

    # Calculate overall progress
    total_modules = sum(course.modules.count() for course in all_courses)
    completed_count = len(completed)
    overall_progress = round(
        (completed_count / total_modules * 100) if total_modules > 0 else 0, 2
    )

    return {
        "completed_modules": completed,
        "current_modules": in_progress,
        "available_modules": all_modules,
        "locked_modules": locked,
        "overall_progress": overall_progress,
        "total_modules": total_modules,
        "completed_count": completed_count,
    }


def get_skill_mastery_data(user):
    """
    Calculate skill mastery across different topics

    Returns:
        Dictionary with:
            - skills: Dict of {skill_name: mastery_percentage}
            - total_quizzes: Total quiz attempts
            - average_score: Average score across all attempts
    """
    attempts = QuizAttempt.objects.filter(user=user)

    if not attempts.exists():
        return {"skills": {}, "total_quizzes": 0, "average_score": 0}

    # Aggregate skill performance
    skill_stats = {}
    total_score = 0

    for attempt in attempts:
        total_score += attempt.score_percentage
        answers = attempt.get_answers()

        for answer in answers:
            try:
                question = Question.objects.get(id=answer["question_id"])
                tags = question.get_tags_list()

                for tag in tags:
                    if tag not in skill_stats:
                        skill_stats[tag] = {"correct": 0, "total": 0}

                    skill_stats[tag]["total"] += 1
                    if answer["is_correct"]:
                        skill_stats[tag]["correct"] += 1
            except Question.DoesNotExist:
                continue

    # Calculate mastery percentages
    skills = {}
    for skill, stats in skill_stats.items():
        mastery = round(
            (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0, 2
        )
        skills[skill] = mastery

    average_score = (
        round(total_score / attempts.count(), 2) if attempts.count() > 0 else 0
    )

    return {
        "skills": skills,
        "total_quizzes": attempts.count(),
        "average_score": average_score,
    }


def get_productivity_trends(user, days=7):
    """
    Get learning productivity trends over time

    Args:
        user: User object
        days: Number of days to analyze (default: 7)

    Returns:
        Dictionary with daily activity data
    """
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)

    attempts = QuizAttempt.objects.filter(
        user=user, attempted_at__gte=start_date, attempted_at__lte=end_date
    ).order_by("attempted_at")

    # Group by date
    daily_data = {}
    for i in range(days):
        date = (end_date - timedelta(days=i)).date()
        daily_data[str(date)] = {"quizzes_taken": 0, "total_score": 0, "time_spent": 0}

    for attempt in attempts:
        date_str = attempt.attempted_at.date()
        if date_str in daily_data:
            daily_data[date_str]["quizzes_taken"] += 1
            daily_data[date_str]["total_score"] += attempt.score_percentage
            daily_data[date_str]["time_spent"] += attempt.time_taken_minutes

    # Calculate averages
    for date, data in daily_data.items():
        if data["quizzes_taken"] > 0:
            data["average_score"] = round(
                data["total_score"] / data["quizzes_taken"], 2
            )
        else:
            data["average_score"] = 0

    return {
        "daily_data": daily_data,
        "total_quizzes": attempts.count(),
        "total_time_hours": round(
            sum(d["time_spent"] for d in daily_data.values()) / 60, 2
        ),
    }


def generate_remediation_plan(user, max_gaps=5):
    """
    Generate personalized remediation plan based on skill gaps

    Args:
        user: User object
        max_gaps: Maximum number of gaps to address

    Returns:
        List of remediation recommendations
    """
    gaps = SkillGap.objects.filter(user=user, is_resolved=False).order_by(
        "current_score"
    )[:max_gaps]

    plan = []
    for gap in gaps:
        # Find relevant modules for this skill
        relevant_modules = Module.objects.filter(
            questions__tags__icontains=gap.skill_name
        ).distinct()

        module_recommendations = []
        for module in relevant_modules:
            if not module.is_locked_for_user(user):
                module_recommendations.append(
                    {"module": module, "reason": f"Covers {gap.skill_name} concepts"}
                )

        plan.append(
            {
                "skill": gap.skill_name,
                "current_score": gap.current_score,
                "target_score": 70,
                "gap_percentage": round(70 - gap.current_score, 2),
                "recommended_modules": module_recommendations[:3],  # Top 3
                "recommended_action": gap.recommended_action,
            }
        )

    return plan
