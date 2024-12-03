from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from rest_framework import viewsets
from .models import Feedback
from .serializers import FeedbackSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

def home(request):
    return render(request, 'feedback/home.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return render(request, 'feedback/register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'feedback/register.html', {'error': 'Username already exists'})

        if User.objects.filter(email=email).exists():
            return render(request, 'feedback/register.html', {'error': 'Email already registered'})

        # Create new user
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('/login/')  # Redirect to dashboard or any page as per your needs

    return render(request, 'feedback/register.html')

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Redirect based on user role
            if user.groups.filter(name='admin').exists():
                return redirect('/admin-dashboard/')
            elif user.groups.filter(name='auditor').exists():
                return redirect('/auditor-dashboard/')
            else:
                return redirect('/dashboard/')
        else:
            return render(request, 'feedback/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'feedback/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# @login_required
# def user_dashboard(request):
#     # Fetch the feedbacks from other users
#     feedback_list = Feedback.objects.filter(is_verified=True).order_by('-created_at')
#     return render(request, 'feedback/user_dashboard.html', {'feedback_list': feedback_list})
@login_required
def user_dashboard(request):
    # Fetch only the verified feedbacks for the logged-in user
    feedback_list = Feedback.objects.filter(is_verified=True).order_by('-created_at')

    # If the user doesn't have any verified feedback yet, show a message
    if not feedback_list:
        feedback_message = "You have not received any verified feedback yet."
    else:
        feedback_message = None  # No message if feedback exists

    return render(request, 'feedback/user_dashboard.html', {'feedback_list': feedback_list, 'feedback_message': feedback_message})



@login_required
def feedback_list(request):
    # Show only feedback added by the logged-in user
    feedback_list = Feedback.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'feedback/feedback-list.html', {'feedback_list': feedback_list})

@login_required
def add_feedback(request):
    if request.method == 'POST':
        comment = request.POST.get('comment')
        if not comment.strip():
            return JsonResponse({'error': 'Feedback comment cannot be empty'}, status=400)
        feedback = Feedback(comment=comment, user=request.user)
        feedback.save()
        return JsonResponse({'status': 'success', 'message': 'Feedback added successfully!'})

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def update_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)

    if feedback.user != request.user:
        return JsonResponse({'error': 'You are not authorized to update this feedback'}, status=403)

    if request.method == 'POST':
        new_comment = request.POST.get('comment')
        if not new_comment.strip():
            return JsonResponse({'error': 'Updated comment cannot be empty'}, status=400)
        feedback.comment = new_comment
        feedback.save()
        return JsonResponse({'status': 'success', 'message': 'Feedback updated successfully', 'data': {'id': feedback.id, 'comment': feedback.comment}})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def delete_feedback(request, feedback_id):
    if request.method == 'POST':
        feedback = get_object_or_404(Feedback, id=feedback_id)

        if feedback.user != request.user:
            return JsonResponse({'error': 'You are not authorized to delete this feedback'}, status=403)

        feedback.delete()
        return JsonResponse({'status': 'success', 'message': 'Feedback deleted successfully!'})

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def auditor_dashboard(request):
    """
    View for Auditor Dashboard to manage feedback verification and deletion.
    """
    if not request.user.groups.filter(name='auditor').exists():
        return JsonResponse({'error': 'Unauthorized access'}, status=403)

    feedback_list = Feedback.objects.all().order_by('-created_at')  # Fetch all feedbacks
    return render(request, 'feedback/auditor_dashboard.html', {'feedback_list': feedback_list})


@csrf_exempt
@login_required
def verify_feedback(request, feedback_id):
    """
    Verify feedback - Auditor-only action.
    """
    if request.method == 'POST' and request.user.groups.filter(name='auditor').exists():
        feedback = get_object_or_404(Feedback, id=feedback_id)
        feedback.is_verified = True
        feedback.save()
        return JsonResponse({'message': 'Feedback verified successfully'})
    return JsonResponse({'error': 'Unauthorized or invalid request'}, status=403)


@csrf_exempt
@login_required
def delete_feedback_auditor(request, feedback_id):
    """
    Delete feedback - Auditor-only action.
    """
    if request.method == 'POST' and request.user.groups.filter(name='auditor').exists():
        feedback = get_object_or_404(Feedback, id=feedback_id)
        feedback.delete()
        return JsonResponse({'message': 'Feedback deleted successfully'})
    return JsonResponse({'error': 'Unauthorized or invalid request'}, status=403)

class FeedbackViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for Feedback.
    Access control is managed based on user roles.
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated] 

    def get_permissions(self):
        """ Handle permissions for CRUD actions. """
        if self.action == 'create':  # Create feedback (POST)
            return []  # No authentication required (open to anyone)
        elif self.action in ['update', 'partial_update']:  # Update feedback (PUT/PATCH)
            # Allow only auditors to verify feedback
            if 'is_verified' in self.request.data and self.request.user.groups.filter(name='auditor').exists():
                return []  # Allow update if the user is an auditor (for verification)
            else:
                return [IsAuthenticated()]  # Anyone can update their own feedback (except for verification)
        elif self.action == 'destroy':  # Delete feedback (DELETE)
            return [IsAuthenticated()]  # Authentication required for deletion
        elif self.action == 'list':  # View feedback (GET list)
            return []  # No authentication required (open to anyone)
        elif self.action == 'retrieve':  # View a specific feedback (GET detail)
            return []  # No authentication required (open to anyone)
        return []  # Default to open permissions for all actions

    def get_queryset(self):
        """ Filter queryset based on user role. """
        user = self.request.user
        if user.groups.filter(name='end-user').exists():
            # End-user can view their own feedback and feedback by others in the common space
            return Feedback.objects.filter(is_verified=True) | Feedback.objects.filter(user=user)
        elif user.groups.filter(name='auditor').exists() or user.groups.filter(name='admin').exists():
            # Auditor and Admin can view all feedback
            return Feedback.objects.all()
        return Feedback.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        
        # Check if the user is authenticated
        if user.is_authenticated:
            serializer.save(user=user)  # Save the feedback with the authenticated user
        else:
            raise PermissionDenied("You must be logged in to submit feedback.")  

    def perform_update(self, serializer):
        """ Allow only auditors to verify feedback. """
        # If the user is an auditor, allow verification to be updated
        if 'is_verified' in self.request.data and self.request.user.groups.filter(name='auditor').exists():
            serializer.save(is_verified=self.request.data.get('is_verified'))
        else:
            # If it's an update by a non-auditor, let them update their feedback without modifying is_verified
            serializer.save()

