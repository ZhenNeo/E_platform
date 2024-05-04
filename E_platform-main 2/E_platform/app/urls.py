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

]