from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(CustomeUser)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Mentorship)
admin.site.register(QuestionPaper)

admin.site.register(Post)
admin.site.register(Comment)

admin.site.register(Week)
admin.site.register(Topic)

admin.site.register(Certificate)

class QuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 1  # Start with one extra form
    show_change_link = True

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]

admin.site.register(QuizResult)
admin.site.register(Grade)