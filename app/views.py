from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, ReceiptForm
from .models import UserProfile,Receipt
from django.contrib.auth.models import User
from django.http import JsonResponse,HttpResponseForbidden



# View for handling user registration. 
def signup(request):
    if request.method == 'POST':
        # Processes the registration form, creates a new user account, and requires admin approval. 

        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  
            user.save()
            is_approved = form.cleaned_data.get('is_approved')
            profile = UserProfile.objects.create(user=user, is_approved=is_approved)

            # Displays success or error messages based on the form validation.

            messages.success(request, "Your account has been successfully created. Wait for the administrators approval")
            return redirect('signin')
        else:
            messages.error(request, "The form is not valid.")
            for field, errors in form.errors.items():
                messages.error(request, f"{field}: {', '.join(errors)}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth.html', {'form': form})


# View for handling user login. 
def signin(request):
    if request.method == 'POST':
        # Authenticates users based on email and password, checks user status, and redirects accordingly. 
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('home')
            elif user.userprofile.is_approved:
                login(request, user)
                return redirect('home')
            else:
                # Provides error messages for incorrect credentials or unapproved accounts.

                messages.error(request, "Your account has not yet been approved by the administrator.")
        else:
            messages.error(request, "Incorrect email or password.")
            
    return render(request, 'auth.html')


# Simple view for logging out users. 

@login_required
def signout(request):
    logout(request)
    return redirect('signin')     # Redirects to the signin page after successfully logging out.


"""
@login_required

def get_users(request):
    users = User.objects.all()
    user_count = users.count()
    user_data = []

    for user in users:
        user_data.append({
            'username': user.username,
            'email': user.email,
        })

    return JsonResponse({'user_count': user_count, 'users': user_data})
"""

# Displays all user accounts for admin management.
# Accessible only by logged-in users, primarily intended for admin users.
@login_required
def admin_page(request):
    users = User.objects.all()  
    
    context = {
        'users': users
    }
    
    return render(request, 'admin.html', context)


@login_required
def accept_user(request, user_id): # Allows admins to approve user accounts.
    # Checks if the requester is a superuser and changes the specified user's status to approved.

    if not request.user.is_superuser: 
        return HttpResponseForbidden('You are not authorized to perform this action.')

    try:
        user = User.objects.get(id=user_id)

        if not user.userprofile.is_approved:
            user.userprofile.is_approved = True
            user.userprofile.save()
            user.is_staff = True

            user.save()
            return JsonResponse({'success': True, 'message': "User successfully accepted."})
        else:
            return JsonResponse({'success': False, 'message': "This user has already been approved."})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': "This user does not exist."})
    



@login_required
def delete_user(request, user_id): # Enables a superuser to delete a user account.
# Verifies superuser status before allowing the deletion of the specified user.

    if not request.user.is_superuser:
        return HttpResponseForbidden('You are not authorized to perform this action.')

    try:
        user_to_delete = User.objects.get(id=user_id)
        
        user_to_delete.delete()
        
        return JsonResponse({'success': True, 'message': "User successfully deleted"})

    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': "This user does not exist."})




@login_required

def home(request): # Displays the home page to the logged-in user, showing a list of distinct receipts.
    # Access restricted to logged-in users, displays user-specific receipt information.
    purchases = Receipt.objects.filter(user=request.user).values_list('purchase_number', flat=True).distinct()
    return render(request, 'home.html', {'purchases': purchases})




@login_required
def receipt_details(request, purchase_number):
    # Accessible only to the user who owns the receipt, ensuring privacy of receipt details.

    receipt = get_object_or_404(Receipt, user=request.user, purchase_number=purchase_number)

# Provides detailed information about a specific receipt in JSON format.
    data = {
        'store_name': receipt.store_name,
        'date_of_purchase': receipt.date_of_purchase,
        'item_list': receipt.item_list,
        'total_amount': receipt.total_amount,
    }
    print("details",data)
    
    return JsonResponse(data)

@login_required

def add_receipt_form(request):
    form = ReceiptForm() # Displays the form for adding a new purchase receipt.

    return render(request, 'add_receipt.html', {'form': form})
@login_required

def add_receipt(request):
    if request.method == 'POST':
        form = ReceiptForm(request.POST) # Handles the addition of new purchase receipts by users. using django form 

        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.user = request.user
            receipt.save()
            return JsonResponse({'success': True, 'message': 'Reçu ajouté avec succès'}) # Validates and saves receipt details, returning success or error messages in JSON.

        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)



@login_required
def delete_receipt(request, purchase_number): # Allows users to delete their own purchase receipts.

    if request.method == 'POST':
        try:
            # Verifies ownership before deletion and provides appropriate success or error messages.
            receipt = Receipt.objects.get(purchase_number=purchase_number, user=request.user)
            receipt.delete()
            return JsonResponse({'success': True, 'message': 'Reçu supprimé avec succès.'})
        except Receipt.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Reçu introuvable.'})
    else:
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'}, status=405)
"""

@login_required
def edit_receipt(request, purchase_number):
    receipt = get_object_or_404(Receipt, purchase_number=purchase_number, user=request.user)
    if request.method == 'POST':
        form = ReceiptForm(request.POST, instance=receipt)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Reçu modifié avec succès'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()})
    else:
        form = ReceiptForm(instance=receipt)
        return render(request, 'modif.html', {'form': form})
    
"""

@login_required
def load_edit_receipt_form(request, purchase_number):
    # Displays the form for editing an existing receipt.

    receipt = get_object_or_404(Receipt, purchase_number=purchase_number, user=request.user)
    form = ReceiptForm(instance=receipt) # Pre-fills the form with the current receipt details for the user to edit.

    return render(request, 'modif.html', {'form': form})

@login_required
def submit_edit_receipt(request, purchase_number):
    # Processes the submission of the edited receipt form.

    receipt = get_object_or_404(Receipt, purchase_number=purchase_number, user=request.user)
    if request.method == 'POST':
        form = ReceiptForm(request.POST, instance=receipt)
        # Validates and saves the updated receipt details, returning JSON responses for success or failure.

        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Reçu modifié avec succès'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()})
