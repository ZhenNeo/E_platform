from django.urls import path
from.views import *


urlpatterns = [
    path('',do_login,name='login'),
    path('student-signup/',student_signup,name='student-signup'),
    path('verify-otp',verify_otp,name='verify_otp'),
    path('logout/', logout_user, name='logout'),
    
    path('course_catalog', course_catalog, name='course_catalog'),
    path('mentorship_page/', homepage, name='mentorship_page'),
    path('paymenthandler/', paymenthandler, name='paymenthandler'),
    path('course/<int:course_id>/', view_course_details, name='view_course_details'),
    path('enroll-course/<int:course_id>/', enroll_course, name='enroll_course'),
    path('course_payment/<int:course_id>/', course_payment, name='course_payment'),
    path('enrolled-courses/', enrolled_course, name='enrolled_course'),
    path('enrolled-courses/<int:course_id>/start-course', start_course, name='start_course'),
    path('start-course/<int:course_id>/previous_question_papers/', previous_question_papers,
         name='previous_question_papers'),
    
    path('community/',community_platform, name='community_platform'),
    path('community/add_post/',add_post, name='add_post'),
    path('community/add_comment/<int:post_id>/',add_comment, name='add_comment'),

    path('like_post/<int:post_id>/',like_post, name='like_post'),
    path('dislike_post/<int:post_id>/',dislike_post, name='dislike_post'),
    path('like_comment/<int:comment_id>/', like_comment, name='like_comment'),
    path('dislike_comment/<int:comment_id>/', dislike_comment, name='dislike_comment'),
    
    path('certificate/', certificate, name='certificates'),
    path('my_courses', all_course_progress, name='my-courses'),
    path('question-papers', question_papers, name='question_papers'),
    path('question-paper/<int:pk>/', view_question_paper, name='view_question_paper'),
    path('question-paper/<int:pk>/download/', download_question_paper, name='download_question_paper'),
    path('course/<int:course_id>/topic/<int:topic_id>/', start_course, name='mark_topic_watched'),
    path('quiz/<int:quiz_id>/', display_quiz, name='display_quiz'),
    
  
]

