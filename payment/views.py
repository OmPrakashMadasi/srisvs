from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from .models import ShippingAddress
from django.contrib import messages


# Create your views here.

def process_order():
    if request.POST:
        payment_form = PaymentForm(request.POST or None)
        # Get shipping session data





    else:
        messages.success(request, 'Access Denied')
        return redirect('index')






def billing_info(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()
        # check to see if user is logged in
        if request.user.is_authenticated:
            # Get the billing form
            billing_form = PaymentForm()
            return render(request, 'billing_info.html', {"cart_products": cart_products,
                                                         "quantities": quantities, "totals": totals,
                                                         "shipping_info": request.POST, "billing_form": billing_form, })
        else:
            # not logged in
            # get the billing Form
            billing_form = PaymentForm()
            return render(request, 'billing_info.html', {"cart_products": cart_products,
                                                         "quantities": quantities, "totals": totals,
                                                         "shipping_info": request.POST, "billing_form": billing_form, })
            shipping_form = request.POST
            return render(request, 'billing_info.html', {"cart_products": cart_products,
                                                         "quantities": quantities, "totals": totals,
                                                         "shipping_info": request.POST, "billing_form": billing_form, })
    else:
        messages.success(request, "Access Denied")
        return redirect('index')


def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    if request.user.is_authenticated:
        #checkout as logged in user
        #shipping User
        shipping_user = ShippingAddress.objects.get(user_id=request.user.id)
        #shipping form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        return render(request, 'checkout.html',
                      {"cart_products": cart_products,
                       "quantities": quantities, "totals": totals, "shipping_form": shipping_form, })
    else:
        #checkout as guest
        shipping_form = ShippingForm(request.POST or None)
        return render(request, 'checkout.html', {"cart_products": cart_products,
                                                 "quantities": quantities, "totals": totals,
                                                 "shipping_form": shipping_form, })


def payment_success(request):
    return render(request, 'payment_success.html')
