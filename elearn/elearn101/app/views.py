from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Enrollment
from django.contrib.auth.models import User
from .models import Usertbl
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def course_catalog(request):
    courses = Course.objects.all()
    return render(request, 'course_catalog.html', {'courses': courses})


def view_course_details(request, course_id):
    course = Course.objects.get(id=course_id)
    return render(request, 'view_course_details.html', {'course': course})


@login_required
def enroll_course(request, course_id):
    if request.method == 'POST':
        # Create a new enrollment record for the current user and course
        Enrollment.objects.create(course_id=course_id, user=request.user)
        # Redirect to the enrolled course page
        return redirect('enrolled_course')
    else:
        # If the request method is not POST, redirect to the course details page
        return redirect('view_course_details', course_id=course_id)



def enrolled_course(request):
    # Retrieve all enrolled courses for the current user
    enrolled_courses = Enrollment.objects.filter(user=request.user)

    return render(request, 'enrolled_course.html', {'enrolled_courses': enrolled_courses})


def signup_login(request):
    return render(request, "signup_login.html")


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if not User.objects.filter(username=username).exists():
            if pass1 == pass2:

                myuser = User.objects.create_user(username=username, password=pass1)
                myuser.save()

                user_tbl = Usertbl(
                    username=username,

                )
                user_tbl.save()
                return render(request, "signup_login.html", {'success_message': "User got Created"})
            else:
                return render(request, "signup_login.html",
                              {'password_error_message': "Check your confirmation password"})
        else:
            return render(request, "signup_login.html", {'username_error_message': "Username Already Exist"})

    return render(request, "signup_login.html")


def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged In!")
            return redirect('course_catalog')

        else:
            messages.success(request, "There was an error, please try again.")
            return redirect('login-error')

    else:
        return render(request, 'signup_login.html', {})


def loginerror(request):
    return render(request, "loginerror.html")


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('signup_login')
