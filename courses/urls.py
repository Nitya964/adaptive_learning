from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),
    # Courses
    path("courses/", views.course_list, name="course_list"),
    path("course/<int:course_id>/", views.course_detail, name="course_detail"),
    # Modules
    path("module/<int:module_id>/", views.module_detail, name="module_detail"),
    # Quiz
    path("quiz/<int:module_id>/start/", views.quiz_start, name="quiz_start"),
    path("quiz/<int:module_id>/submit/", views.quiz_submit, name="quiz_submit"),
    # Analytics & Learning Path
    path("analytics/", views.analytics, name="analytics"),
    path("learning-path/", views.learning_path, name="learning_path"),
    # API Endpoints
    path("api/skill-mastery/", views.api_skill_mastery, name="api_skill_mastery"),
    path("api/productivity/", views.api_productivity_data, name="api_productivity"),
    path("api/knowledge-map/", views.api_knowledge_map, name="api_knowledge_map"),
]
