from django.shortcuts import render, redirect
from .models import Product, Category, Profile, Testimonial, VisitorCount
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from django import forms
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django.db.models import Q
import json
from cart.cart import Cart


# Create your views here.


def testimonials(request):
    total_customers = Testimonial.objects.count()
    happy_customers = Testimonial.objects.filter(rating__gte=4).count()
    reviews = Testimonial.objects.all()[:5]

    context = {
        'total_customers': total_customers,
        'happy_customers': happy_customers,
        'reviews': reviews,
    }
    return render(request, 'index.html', context)


def search(request):
    query = request.GET.get('searched', '')  # Get the search query from the GET request
    if query:
        # Query the Product model to find matches
        searched = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))

        # Check if any products were found
        if searched.exists():
            return render(request, 'search.html', {'searched': searched, 'query': query})
        else:
            messages.error(request, "That product does not exist. Please try again.")
            return render(request, 'search.html', {'query': query})
    else:
        return render(request, 'search.html', {})


def update_info(request):
    if request.user.is_authenticated:
        # Get current user's profile
        try:
            current_user = Profile.objects.get(user_id=request.user.id)
        except Profile.DoesNotExist:
            messages.error(request, "Profile does not exist.")
            return redirect('index')

        # Get current user's shipping info, or handle if it doesn't exist
        try:
            shipping_user = ShippingAddress.objects.get(user_id=request.user.id)
        except ShippingAddress.DoesNotExist:
            shipping_user = None

        # Instantiate forms
        form = UserInfoForm(request.POST or None, instance=current_user)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        if form.is_valid() and shipping_form.is_valid():
            form.save()
            shipping_form.save()
            messages.success(request, 'Your info has been updated!')
            return redirect('index')

        return render(request, "update_info.html", {
            'form': form,
            'shipping_form': shipping_form
        })

    else:
        messages.error(request, "Please login to update your account.")
        return redirect('index')


def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # did the form is filled?
        if request.method == 'POST':
            #proceed with it
            form = ChangePasswordForm(current_user, request.POST)
            # is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been updated!')
                #login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')

        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html', {'form': form})
    else:
        messages.success(request, 'Please login to Proceed')
        return redirect('index')


def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        if request.method == 'POST':
            user_form = UpdateUserForm(request.POST, request.FILES, instance=current_user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Your account has been updated!')
                return redirect('index')
        else:
            user_form = UpdateUserForm(instance=current_user)
        return render(request, "update_user.html", {'user_form': user_form})
    else:
        messages.success(request, "Please Login to Update Your Account ")
        return redirect('index')


def category(request, foo):
    foo = foo.replace('-', '')
    try:
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})

    except:
        messages.error(request, 'That Category does not exist')
        return redirect('index')


def index(request):
    products = Product.objects.all()
    # visitor count increment by 1
    visitor_count, created = VisitorCount.objects.get_or_create(id=1)
    # visitor_count.count = 0
    # visitor_count.save()
    visitor_count.increment() # Increment the visit count
    testimonials = Testimonial.objects.all()
    total_customers_deafult = 2000
    total_customers = testimonials.count() + visitor_count.count + total_customers_deafult
    # Set default count for happy customers if no testimonials are present
    happy_customers_default = 1500  # Example default value
    happy_customers = testimonials.filter(rating__gte=4).count() + visitor_count.count + happy_customers_default
    # Format counts with commas
    formatted_total_customers = "{:,}".format(total_customers)
    formatted_happy_customers = "{:,}".format(happy_customers)

    # happy_customers = testimonials.filter(rating__gte=4).count() + visitor_count.count
    reviews = Testimonial.objects.all()[:5]
    return render(request, 'index.html',
                  {'products': products,
                   'testimonials': testimonials,
                   'total_customers': formatted_total_customers,
                   'happy_customers': formatted_happy_customers,
                   'reviews': reviews,
                   })


def all_products(request):
    products = Product.objects.all()
    return render(request, 'category.html', {'products': products})


def product(request, pk):
    products = Product.objects.filter(id=pk)
    return render(request, 'product.html', {'products': products})


def special_products(request):
    products = Product.objects.all()
    return render(request, 'special-products.html', {'products': products})


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            #do some shopping cart
            current_user = Profile.objects.get(user_id=request.user.id)
            #get their saved cart from database
            saved_cart = current_user.old_cart
            #convert database string to python dictionary
            if saved_cart:
                #convert to dictionary using json
                converted_cart = json.loads(saved_cart)
                #add the loaded cart dictionary to our session
                #get the cart
                cart = Cart(request)
                #loop through the cart and add the tems from the database
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            messages.success(request, 'Login is successful...!!')
            return redirect('index')
        else:
            messages.success(request, 'There was an error')
            return redirect('login')
    else:
        return render(request, 'login.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, ("You have successfully logged out...!!"))
    return redirect('index')


def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            #log in user
            user = authenticate(request, username=username, password=password)
            login(request, user)
            messages.success(request, 'Username Created - Please Fill the Details...')
            return redirect('update_info')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
                return redirect('register')
    else:
        return render(request, 'register.html', {'form': form})

#           if user is not None:
#               login(request, user)  # Log the user in
#               messages.success(request, 'You are now logged in!')
#               return redirect('index')  # Redirect to the homepage
#           else:
#                for error in list(form.errors.values()):
#                   messages.error(request, error)
#                   return redirect('login')  # Redirect to the login page
#       else:
#           messages.error(request, 'There was an error with your registration.')
#           return render(request, 'register.html', {'form': form})
#  else:
#       form = SignUpForm()

#   return render(request, 'register.html', {'form': form})
