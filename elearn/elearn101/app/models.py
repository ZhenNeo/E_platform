from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    TECH_COURSE = 'Tech Courses'
    CBSE_COURSE = 'CBSE Courses'
    CATEGORY_CHOICES = [
        (TECH_COURSE, 'Tech Courses'),
        (CBSE_COURSE, 'CBSE Courses'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default=TECH_COURSE)
    grade = models.CharField(max_length=10, blank=True, null=True)
    image = models.ImageField(upload_to='staticfiles/course_images/', null=True, blank=True)

    def __str__(self):
        return self.title


class Student(models.Model):
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"


class Mentorship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    reason = models.TextField()
    phone_number = models.CharField(max_length=15)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # Assuming each mentorship is associated with a course
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mentorship for {self.user.username}"
