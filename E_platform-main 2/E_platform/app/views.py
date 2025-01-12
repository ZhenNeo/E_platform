from django.contrib.auth import get_user_model
from .forms import *
import random
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404, redirect
from .models import Course, Enrollment, QuestionPaper
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest, FileResponse, HttpResponse
from django.http import JsonResponse, Http404
from .models import Post, Comment
from django.utils import timezone

    
@login_required
def all_course_progress(request):
    student = Student.objects.get(user=request.user)
    enrollments = Enrollment.objects.filter(user=student)
    
    course_progress_data = []
    
    for enrollment in enrollments:
        course = enrollment.course
        total_topics = sum(week.topics.count() for week in course.weeks.all())
        watched_topics = sum(topic.watched_by_users.filter(id=student.id).exists() for week in course.weeks.all() for topic in week.topics.all())

        if total_topics > 0:
            progress_percentage = round((watched_topics / total_topics) * 100)
        else:
            progress_percentage = 0
        
        course_progress_data.append({
            'course': course,
            'total_topics': total_topics,
            'watched_topics': watched_topics,
            'progress_percentage': progress_percentage,
        })

    filter_status = request.GET.get('status', 'in_progress')
    if filter_status == 'completed':
        filtered_courses = [data for data in course_progress_data if data['progress_percentage'] == 100]
    else:
        filtered_courses = [data for data in course_progress_data if data['progress_percentage'] < 100]

    context = {
        'course_progress_data': filtered_courses,
        'filter_status': filter_status,
    }
    
    return render(request, 'my_courses.html', context)


def question_papers(request):
    selected_grade = request.GET.get('grade')

    question_papers = QuestionPaper.objects.all()
    if selected_grade:
        question_papers = question_papers.filter(grade=selected_grade)

    grades = QuestionPaper.objects.values_list('grade', flat=True).distinct()

    context = {
        'question_papers': question_papers,
        'selected_grade': selected_grade,
        'grades': sorted(grades)
    }

    return render(request, 'question_paper.html', context)

def view_question_paper(request, pk):
    question_paper = get_object_or_404(QuestionPaper, pk=pk)
    return FileResponse(question_paper.file.open(), content_type='application/pdf')

def download_question_paper(request, pk):
    question_paper = get_object_or_404(QuestionPaper, pk=pk)
    response = FileResponse(question_paper.file.open(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{question_paper.title}.pdf"'
    return response

@login_required
def start_course(request, course_id):
    user = Student.objects.get(user=request.user)
    course = get_object_or_404(Course, id=course_id)
    
    weeks = Week.objects.filter(course=course).prefetch_related('topics')
    
    watched_topics = Topic.objects.filter(watched_by_users=user, week__course=course)
    unlocked_quizzes = Quiz.objects.filter(topic__in=watched_topics)
    
    quizzes_data = []
    for quiz in unlocked_quizzes:
        quizzes_data.append({
            'quiz_id': quiz.id,
            'video_title': quiz.topic.title,
            'status': 'Unlocked' if user in quiz.topic.watched_by_users.all() else 'Locked',
            'due_date': quiz.due_date,
            'weight': quiz.weight,
            'score': round(quiz.results.get(student=user).score / quiz.results.get(student=user).total_questions * 100, 2) if quiz.results.filter(student=user).exists() else 'N/A'
        })

    return render(request, 'start_course.html', {
        'course': course,
        'weeks': weeks,
        'quizzes_data': quizzes_data,
        'quizzes': unlocked_quizzes,
    })

def watch_topic(request, course_id, topic_id):
    user = Student.objects.get(user=request.user)
    course = get_object_or_404(Course, id=course_id)
    topic = get_object_or_404(Topic, id=topic_id)
    
    topic.watched_by_users.add(user)
    
    weeks = Week.objects.filter(course=course).prefetch_related('topics')
    
    all_topics = Topic.objects.filter(week__course=course)  # Fetch all topics related to the course
    
    return render(request, 'watch_topic.html', {
        'course': course,
        'weeks': weeks,
        'current_topic': topic,
        'all_topics': all_topics  # Pass all topics to the template
    })


@login_required
def display_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.quiz_questions.all().order_by('question_no')
    student = Student.objects.get(user=request.user)

    if request.method == 'POST':
        score = 0
        total_questions = questions.count()

        for question in questions:
            selected_option = request.POST.get(f'question_{question.id}')
            if selected_option == question.correct_option:
                score += 1

            # Save or update the selected answers
            selected_answer, created = SelectedAnswer.objects.update_or_create(
                student=student,
                quiz=quiz,
                question=question,
                defaults={'selected_option': selected_option}
            )

        # Save or update the quiz result
        QuizResult.objects.update_or_create(
            student=student,
            quiz=quiz,
            defaults={
                'score': score,
                'total_questions': total_questions,
                'completed_at': timezone.now()  
            }
        )

    return render(request, 'quiz_detail.html', {
        'quiz': quiz,
        'questions': questions
    })

@login_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    student = Student.objects.get(user=request.user)
    questions = quiz.quiz_questions.all().order_by('question_no')
    quiz_result = get_object_or_404(QuizResult, quiz=quiz, student=student)
    selected_answers = SelectedAnswer.objects.filter(student=student, quiz=quiz).select_related('question')

    # Calculate percentage score
    total_questions = questions.count()
    percentage_score = round((quiz_result.score / total_questions) * 100, 2)

    return render(request, 'quiz_result.html', {
        'quiz': quiz,
        'questions': questions,
        'quiz_result': quiz_result,
        'selected_answers': selected_answers,
        'percentage_score': percentage_score,  # Pass percentage score to the template
    })


def calculate_grade_for_student(student):
    courses = Course.objects.filter(quizzes__results__student=student).distinct()

    for course in courses:
        quizzes = Quiz.objects.filter(course=course)
        total_weighted_score = 0.0

        for quiz in quizzes:
            quiz_results = QuizResult.objects.filter(student=student, quiz=quiz)
            if quiz_results.exists():
                quiz_result = quiz_results.latest('completed_at')
                weighted_score = (quiz_result.score / quiz_result.total_questions) * quiz.weight
                total_weighted_score += weighted_score

        final_grade = calculate_grade_from_score(total_weighted_score)

        certificate, created = Certificate.objects.get_or_create(user=student, course=course)
        Grade.objects.update_or_create(
            certificate=certificate,
            defaults={'grade': final_grade}
        )


def calculate_grade_from_score(score):
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'

@login_required
def download_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id, user__user=request.user)
    if not certificate.certificate_image:
        raise Http404("Certificate image not found")
    
    # Open the image file
    file_path = certificate.certificate_image.path
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='image/jpeg')
        response['Content-Disposition'] = f'attachment; filename="{certificate.user.Full_Name} certificate {certificate.course.title}.jpg"'
        return response
    

@login_required
def certificate(request):
    user = Student.objects.get(user=request.user)
    
    # Calculate grades for the student
    calculate_grade_for_student(user)    

    certificates = Certificate.objects.filter(user=user)
    courses_with_certificates = {}

    # Group certificates by course and include grade
    for certificate in certificates:
        grade = Grade.objects.filter(certificate=certificate).first()
        courses_with_certificates[certificate.course] = {
            'certificate': certificate,
            'grade': grade.grade if grade else 'N/A'
        }

    return render(request, 'certificates.html', {'courses_with_certificates': courses_with_certificates})

# ---------------------------------------------------------------------------
# Login view
# ---------------------------------------------------------------------------
def do_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():

            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                user_type = user.user_type
                if user_type == 1:  # Assuming user_type is an integer field
                    return redirect('admin')
                elif user_type == 2:
                    return redirect('course_catalog')
                elif user_type == 3:
                    return HttpResponse('course provider')
                else:
                    messages.error(request, "Invalid Login!")
            else:
                messages.error(request, "Invalid Login!")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def generate_otp():
    return random.randint(100000, 999999)


def send_otp(email, otp):
    send_mail(
        'Email Verification OTP',
        f'Your OTP is: {otp}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )


def student_signup(request):
    if request.method == 'POST':
        form = AdminForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['EmailID']

            # Check if the email already exists
            if get_user_model().objects.filter(email=user_email).exists():
                messages.error(request, 'This email is already in use.')
                return redirect('student-signup')  # Redirect back to the signup page

            # Create a new user instance
            user = get_user_model().objects.create_user(
                email=user_email,
                password=form.cleaned_data['password1'],
                username=user_email,  # You can set username as email if you want
                user_type=2
            )
            # Generate a random OTP and send it to the user's email
            otp = generate_otp()

            # Send the OTP to the user's email
            send_otp(user_email, otp)

            # Save the OTP in the session
            request.session['otp'] = otp
            request.session['email'] = user_email

            return redirect('verify_otp')
    else:
        form = AdminForm()

    return render(request, 'student_signup.html', {'form': form})


def logout_user(request):
    return redirect('login')


def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        if entered_otp == str(stored_otp):
            # OTP verification successful
            email = request.session.get('email')
            Full_Name = request.POST.get('Full_Name')

            # Create a student profile
            user = get_user_model().objects.get(email=email)
            student_profile = Student.objects.create(user=user,
                                                     Full_Name=user.email)
            # Redirect to a success page
            return redirect('course_catalog')

    # OTP verification failed or GET request
    return render(request, 'verify_otp.html')


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


def course_payment(request, course_id):
    currency = 'INR'
    amount = 20000  # Rs. 200

    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))

    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'paymenthandler/'

    # we need to pass these details to frontend.
    context = {}
    context['course_id'] = course_id
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url
    return render(request, 'course_payment.html', context)


@login_required
def enrolled_course(request):
    try:
        # Retrieve the Admin instance associated with the current user
        admin_user = Student.objects.get(user=request.user)
        # Retrieve enrolled courses for the admin user
        enrolled_courses = Enrollment.objects.filter(user=admin_user)
    except Student.DoesNotExist:
        # Handle the case where the user is not an admin
        enrolled_courses = []

    return render(request, 'enrolled_course.html', {'enrolled_courses': enrolled_courses})


# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


def homepage(request):
    currency = 'INR'
    amount = 20000  # Rs. 200

    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))

    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'paymenthandler/'

    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url

    return render(request, 'mentorship_page.html', context=context)


# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.
@csrf_exempt
def paymenthandler(request):
    # only accept POST request.
    if request.method == "POST":
        try:

            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                amount = 20000  # Rs. 200
                try:

                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)

                    # render success page on successful caputre of payment
                    return render(request, 'paymentsuccess.html')
                except:

                    # if there is an error while capturing payment.
                    return render(request, 'paymentfail.html')
            else:

                # if signature verification fails.
                return render(request, 'paymentfail.html')
        except:

            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
        # if other than POST request is made.
        return HttpResponseBadRequest()


@login_required
def community_platform(request):
    # Retrieve all posts for display
    posts = Post.objects.all()
    return render(request, 'community_platform.html', {'posts': posts})


@login_required
def add_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        user = request.user.student  # Get the Student instance associated with the logged-in user
        post = Post.objects.create(user=user, content=content)
        return redirect('community_platform')
    return render(request, 'add_post.html')


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        user = request.user.student  # Get the Student instance associated with the logged-in user
        comment = Comment.objects.create(post=post, user=user, content=content)
        return redirect('community_platform')
    return render(request, 'add_comment.html', {'post': post})

def previous_question_papers(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    question_paper = QuestionPaper.objects.filter(course=course).first()

    if question_paper:
        # Assuming there's only one question paper per course for simplicity
        file_path = question_paper.file.path
        # Open the file and serve it as a download response
        response = FileResponse(open(file_path, 'rb'))
        # Set the content type header to force the browser to download the file
        response['Content-Disposition'] = f'attachment; filename="{question_paper.title}.pdf"'
        return response
    else:
        # Handle the case where no question paper is found
        return HttpResponse("No question paper found for this course.", status=404)

def like_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.likes += 1
    post.save()
    return JsonResponse({'likes': post.likes})


def dislike_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.dislikes += 1
    post.save()
    return JsonResponse({'dislikes': post.dislikes})


def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.likes += 1
    comment.save()
    return JsonResponse({'likes': comment.likes})


def dislike_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.dislikes += 1
    comment.save()
    return JsonResponse({'dislikes': comment.dislikes})


