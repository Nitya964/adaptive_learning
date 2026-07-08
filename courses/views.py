from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from .models import Course, Module, Question, UserProgress, QuizAttempt, SkillGap
from .adaptive_engine import (
    analyze_performance,
    get_user_knowledge_map,
    get_skill_mastery_data,
    get_productivity_trends,
    generate_remediation_plan,
)
import json


def login_view(request):
    """
    User login view
    Handles both GET (display form) and POST (authenticate user)
    """
    if request.user.is_authenticated:
        return redirect("courses:dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("courses:dashboard")
        else:
            context = {
                "error": "Invalid username or password",
            }
            return render(request, "courses/login.html", context)

    return render(request, "courses/login.html")


def logout_view(request):
    """
    User logout view
    Logs out the user and redirects to login page
    """
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    """
    Main Dashboard - Personalized Learning Hub
    Shows knowledge map, skill radar chart, and recommendations
    """
    # Get user's knowledge map
    knowledge_map = get_user_knowledge_map(request.user)

    # Get skill mastery data for radar chart
    skill_data = get_skill_mastery_data(request.user)

    # Get productivity trends (last 7 days)
    productivity = get_productivity_trends(request.user, days=7)

    # Generate remediation plan
    remediation = generate_remediation_plan(request.user)

    # Get recent quiz attempts
    recent_attempts = QuizAttempt.objects.filter(user=request.user).order_by(
        "-attempted_at"
    )[:5]

    # Get active courses
    all_courses = Course.objects.all()

    context = {
        "knowledge_map": knowledge_map,
        "skill_data": skill_data,
        "productivity": productivity,
        "remediation": remediation,
        "recent_attempts": recent_attempts,
        "courses": all_courses,
    }
    return render(request, "courses/dashboard.html", context)


@login_required
def course_list(request):
    """
    List all available courses
    """
    courses = Course.objects.all()

    # Add progress info for each course
    for course in courses:
        total_modules = course.modules.count()
        completed_modules = UserProgress.objects.filter(
            user=request.user, module__course=course, completed=True
        ).count()
        course.progress_percentage = round(
            (completed_modules / total_modules * 100) if total_modules > 0 else 0, 2
        )

    context = {
        "courses": courses,
    }
    return render(request, "courses/course_list.html", context)


@login_required
def course_detail(request, course_id):
    """
    Course detail with learning path visualization
    Shows modules in order with lock/unlock status
    """
    course = get_object_or_404(Course, id=course_id)
    modules = course.get_modules_ordered()

    # Add lock status and progress for each module
    modules_with_status = []
    for module in modules:
        try:
            progress = UserProgress.objects.get(user=request.user, module=module)
            is_completed = progress.completed
            score = progress.score
        except UserProgress.DoesNotExist:
            is_completed = False
            score = 0

        is_locked = module.is_locked_for_user(request.user)

        modules_with_status.append(
            {
                "module": module,
                "is_locked": is_locked,
                "is_completed": is_completed,
                "score": score,
            }
        )

    context = {
        "course": course,
        "modules_with_status": modules_with_status,
    }
    return render(request, "courses/course_detail.html", context)


@login_required
def module_detail(request, module_id):
    """
    Module detail page
    Shows module info and start quiz button
    """
    module = get_object_or_404(Module, id=module_id)

    # Check if module is locked
    if module.is_locked_for_user(request.user):
        return redirect("course_detail", course_id=module.course.id)

    # Get user's progress
    try:
        progress = UserProgress.objects.get(user=request.user, module=module)
    except UserProgress.DoesNotExist:
        progress = None

    # Get questions preview (first 3)
    questions_preview = module.questions.all()[:3]
    total_questions = module.questions.count()

    context = {
        "module": module,
        "progress": progress,
        "questions_preview": questions_preview,
        "total_questions": total_questions,
    }
    return render(request, "courses/module_detail.html", context)


@login_required
def quiz_start(request, module_id):
    """
    Start a quiz - selects questions adaptively based on user level
    """
    module = get_object_or_404(Module, id=module_id)

    # Check if module is locked
    if module.is_locked_for_user(request.user):
        return redirect("course_detail", course_id=module.course.id)

    # Get user's current level for this module
    try:
        progress = UserProgress.objects.get(user=request.user, module=module)
        current_level = progress.current_level
    except UserProgress.DoesNotExist:
        current_level = "beginner"

    # Adaptive question selection
    # Select questions based on difficulty level
    difficulty_scores = {
        "beginner": (1, 50),
        "intermediate": (51, 75),
        "advanced": (76, 100),
    }

    min_diff, max_diff = difficulty_scores.get(current_level, (1, 50))

    # Get questions within user's difficulty range
    # Randomize selection so repeated attempts do not always show the exact same items.
    questions = Question.objects.filter(
        module=module, difficulty_score__gte=min_diff, difficulty_score__lte=max_diff
    ).order_by("?")[:10]  # Limit to 10 questions per quiz

    if not questions.exists():
        # Fallback: get any questions from this module
        questions = module.questions.order_by("?")[:10]

    # Store quiz start time in session
    request.session["quiz_start_time"] = timezone.now().isoformat()
    request.session["quiz_module_id"] = module.id

    context = {
        "module": module,
        "questions": questions,
        "current_level": current_level,
        "total_questions": questions.count(),
    }
    return render(request, "courses/quiz.html", context)


@login_required
def quiz_submit(request, module_id):
    """
    Process quiz submission and analyze performance
    """
    if request.method != "POST":
        return redirect("quiz_start", module_id=module_id)

    module = get_object_or_404(Module, id=module_id)

    # Get quiz start time from session
    quiz_start_time_str = request.session.get("quiz_start_time")
    if not quiz_start_time_str:
        return redirect("dashboard")

    quiz_start_time = datetime.fromisoformat(quiz_start_time_str)
    time_taken_minutes = round(
        (timezone.now() - quiz_start_time).total_seconds() / 60, 2
    )

    # Get user answers
    user_answers = request.POST.dict()

    # Process answers
    answers_list = []
    correct_count = 0
    total_questions = 0

    for key, value in user_answers.items():
        if key.startswith("question_"):
            question_id = int(key.split("_")[1])
            question = get_object_or_404(Question, id=question_id)

            is_correct = question.check_answer(value)
            if is_correct:
                correct_count += 1

            answers_list.append(
                {
                    "question_id": question_id,
                    "user_answer": value,
                    "correct_answer": question.correct_answer,
                    "is_correct": is_correct,
                }
            )

            total_questions += 1

    # Calculate score
    score_percentage = round(
        (correct_count / total_questions * 100) if total_questions > 0 else 0, 2
    )

    # Get user's current level
    try:
        progress = UserProgress.objects.get(user=request.user, module=module)
        current_level = progress.current_level
    except UserProgress.DoesNotExist:
        current_level = "beginner"

    # Create QuizAttempt record
    quiz_attempt = QuizAttempt.objects.create(
        user=request.user,
        module=module,
        total_questions=total_questions,
        correct_answers=correct_count,
        score_percentage=score_percentage,
        time_taken_minutes=time_taken_minutes,
        adaptive_level=current_level,
    )
    quiz_attempt.save_answers(answers_list)

    # Run AI Analysis
    analysis = analyze_performance(
        user=request.user,
        module=module,
        quiz_score=score_percentage,
        time_taken_minutes=time_taken_minutes,
        quiz_attempt=quiz_attempt,
    )

    # Clear quiz session data
    if "quiz_start_time" in request.session:
        del request.session["quiz_start_time"]
    if "quiz_module_id" in request.session:
        del request.session["quiz_module_id"]

    context = {
        "module": module,
        "score": score_percentage,
        "correct_count": correct_count,
        "total_questions": total_questions,
        "time_taken": time_taken_minutes,
        "analysis": analysis,
        "answers": answers_list,
        "quiz_attempt": quiz_attempt,
    }

    return render(request, "courses/quiz_result.html", context)


@login_required
def analytics(request):
    """
    Detailed analytics view
    Shows charts and detailed progress metrics
    """
    # Get skill mastery data
    skill_data = get_skill_mastery_data(request.user)

    # Get productivity trends (30 days)
    productivity = get_productivity_trends(request.user, days=30)

    # Get all quiz attempts
    all_attempts = QuizAttempt.objects.filter(user=request.user).order_by(
        "-attempted_at"
    )

    # Calculate statistics
    total_time_hours = sum(a.time_taken_minutes for a in all_attempts) / 60
    average_score = (
        sum(a.score_percentage for a in all_attempts) / all_attempts.count()
        if all_attempts.exists()
        else 0
    )

    # Get skill gaps
    skill_gaps = SkillGap.objects.filter(user=request.user, is_resolved=False).order_by(
        "current_score"
    )[:10]

    context = {
        "skill_data": skill_data,
        "productivity": productivity,
        "all_attempts": all_attempts[:20],  # Recent 20
        "total_quizzes": all_attempts.count(),
        "total_time_hours": round(total_time_hours, 2),
        "average_score": round(average_score, 2),
        "skill_gaps": skill_gaps,
    }
    return render(request, "courses/analytics.html", context)


@login_required
def learning_path(request):
    """
    Visual learning path showing all courses and modules
    """
    knowledge_map = get_user_knowledge_map(request.user)

    context = {
        "knowledge_map": knowledge_map,
    }
    return render(request, "courses/learning_path.html", context)


# API Endpoints
@login_required
def api_skill_mastery(request):
    """
    API endpoint for skill mastery chart data
    """
    skill_data = get_skill_mastery_data(request.user)

    # Format for Chart.js radar chart
    labels = list(skill_data["skills"].keys())
    data = list(skill_data["skills"].values())

    return JsonResponse(
        {
            "labels": labels,
            "data": data,
            "total_quizzes": skill_data["total_quizzes"],
            "average_score": skill_data["average_score"],
        }
    )


@login_required
def api_productivity_data(request):
    """
    API endpoint for productivity chart data
    """
    days = request.GET.get("days", 7)
    try:
        days = int(days)
    except ValueError:
        days = 7

    productivity = get_productivity_trends(request.user, days=days)

    # Format for Chart.js line chart
    dates = list(productivity["daily_data"].keys())
    scores = [productivity["daily_data"][d]["average_score"] for d in dates]
    quizzes_taken = [productivity["daily_data"][d]["quizzes_taken"] for d in dates]

    return JsonResponse(
        {
            "dates": dates,
            "scores": scores,
            "quizzes_taken": quizzes_taken,
            "total_quizzes": productivity["total_quizzes"],
            "total_time_hours": productivity["total_time_hours"],
        }
    )


@login_required
def api_knowledge_map(request):
    """
    API endpoint for knowledge map data
    """
    knowledge_map = get_user_knowledge_map(request.user)

    completed = [
        {
            "id": m.id,
            "title": m.title,
            "difficulty": m.difficulty_level,
            "course": m.course.title,
        }
        for m in knowledge_map["completed_modules"]
    ]

    in_progress = [
        {
            "id": m.id,
            "title": m.title,
            "difficulty": m.difficulty_level,
            "course": m.course.title,
        }
        for m in knowledge_map["current_modules"]
    ]

    available = [
        {
            "id": m.id,
            "title": m.title,
            "difficulty": m.difficulty_level,
            "course": m.course.title,
        }
        for m in knowledge_map["available_modules"]
    ]

    locked = [
        {
            "id": m.id,
            "title": m.title,
            "difficulty": m.difficulty_level,
            "course": m.course.title,
        }
        for m in knowledge_map["locked_modules"]
    ]

    return JsonResponse(
        {
            "completed": completed,
            "in_progress": in_progress,
            "available": available,
            "locked": locked,
            "overall_progress": knowledge_map["overall_progress"],
            "total_modules": knowledge_map["total_modules"],
            "completed_count": knowledge_map["completed_count"],
        }
    )
