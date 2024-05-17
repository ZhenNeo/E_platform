from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomeUser(AbstractUser):
    email = models.EmailField(unique=True)
    user_type_choices = ((1, 'ADMIN'),
                         (2, 'STUDENT'),
                         (3, 'COURSE PROVIDER'))
    user_type = models.IntegerField(choices=user_type_choices, default=1)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Student(models.Model):
    user = models.OneToOneField(CustomeUser, on_delete=models.CASCADE)
    Full_Name = models.CharField(max_length=20)
    Mobile_no = models.CharField(max_length=10)
    EmailID = models.EmailField(max_length=255)
    DOB = models.DateField(null=True, blank=True)
    Gender_choices = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Others')
    )
    Gender = models.CharField(max_length=10, choices=Gender_choices, default='M')

    def __str__(self) -> str:
        return self.Full_Name



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
    demo_video = models.FileField(upload_to='staticfiles/demo_videos/', null=True, blank=True)
    course_video = models.FileField(upload_to='staticfiles/course_videos/', null=True, blank=True)

    def __str__(self):
        return self.title

class Week(models.Model):
    course = models.ForeignKey(Course, related_name='weeks', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Week {self.number}: {self.title}"

class Topic(models.Model):
    week = models.ForeignKey(Week, related_name='topics', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    video = models.FileField(upload_to='staticfiles/topic_videos/', null=True, blank=True)
    watched_by_users = models.ManyToManyField(Student, blank=True)

    def __str__(self):
        return self.title

class StudentCourseProgress(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed_weeks = models.ManyToManyField(Week, blank=True)
        

class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.user} enrolled in {self.course.title}"


class Mentorship(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    reason = models.TextField()
    phone_number = models.CharField(max_length=15)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # Assuming each mentorship is associated with a course
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mentorship for {self.user.username}"


class QuestionPaper(models.Model):
    title = models.CharField(max_length=200)
    year = models.IntegerField()
    subject = models.CharField(max_length=100)
    file = models.FileField(upload_to='question_papers/')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Post(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)


class Certificate(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completion_date = models.DateTimeField(auto_now_add=True)
    certificate_image = models.ImageField(upload_to='staticfiles/certificates/')

    def __str__(self):
        return f"{self.user.Full_Name}'s Certificate for {self.course.title}"