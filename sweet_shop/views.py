from django.shortcuts import render, redirect, get_object_or_404
from .models import Sweet, Order
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

def home(request):
    sweets = Sweet.objects.all()
    return render(request, 'sweet_shop/home.html', {'sweets': sweets})

# @login_required
from django.http import HttpResponseBadRequest


@login_required
def place_order(request, sweet_id):
    sweet = get_object_or_404(Sweet, id=sweet_id)

    if request.method == "POST":
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            messages.error(request, "Invalid quantity entered.")
            return redirect('home')

        if quantity <= 0:
            messages.error(request, "Quantity must be at least 1.")
        elif quantity > sweet.quantity:
            messages.error(request, f"❌ Only {sweet.quantity} pieces of {sweet.name} available.")
        else:
            # create multiple orders (or one with quantity — depends on your model design)
            Order.objects.create(user=request.user, sweet=sweet)
            sweet.quantity -= quantity
            sweet.save()
            messages.success(request, f"✅ Order placed for {quantity} {sweet.name}(s)!")

    return redirect('home')

from django.contrib import messages

@login_required
def place_order(request, sweet_id):
    sweet = get_object_or_404(Sweet, id=sweet_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        if sweet.quantity_available >= quantity:
            # Place the order
            Order.objects.create(user=request.user, sweet=sweet, quantity=quantity)
            sweet.quantity_available -= quantity
            sweet.save()
            messages.success(request, f"Order placed for {quantity} {sweet.name}(s)!")
        else:
            messages.error(request, f"Only {sweet.quantity_available} {sweet.name}(s) available!")

    return redirect('home')

@login_required
def view_orders(request):
    orders = Order.objects.all()
    return render(request, 'sweet_shop/orders.html', {'orders': orders})

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import HttpResponse

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after register
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'sweet_shop/register.html', {'form': form})
