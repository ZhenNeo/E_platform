from django.contrib import admin
from .models import Course, Usertbl, Enrollment

admin.site.register(Course)
admin.site.register(Usertbl)
admin.site.register(Enrollment)