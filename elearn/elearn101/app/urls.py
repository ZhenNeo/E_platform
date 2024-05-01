from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_catalog, name='course_catalog'),
    path('mentorship_page/', views.homepage, name='mentorship_page'),
    path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
    path('course/<int:course_id>/', views.view_course_details, name='view_course_details'),
    path('enroll-course/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('course_payment/<int:course_id>/', views.course_payment, name='course_payment'),
    path('enrolled-courses/', views.enrolled_course, name='enrolled_course'),
    path("signup_login", views.signup_login, name="signup_login"),
    path('signup', views.signup, name='signup'),
    path('user_login', views.user_login, name='user_login'),
    path("loginerror", views.loginerror, name="login-error"),
    path('logout/', views.logout_user, name='logout'),
    path('enrolled-courses/<int:course_id>/start-course', views.start_course, name='start_course'),
    path('start-course/<int:course_id>/previous_question_papers/', views.previous_question_papers, name='previous_question_papers'),
]
