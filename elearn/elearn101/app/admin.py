from django.contrib import admin
from .models import Course, Student, Enrollment, Mentorship, QuestionPaper

admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Enrollment)
admin.site.register(Mentorship)
admin.site.register(QuestionPaper)

