from django.shortcuts import render, redirect, get_object_or_404
from . import models
from django.http import JsonResponse
import json
import datetime
from .utils import cookieCart, cartData
from django.contrib.auth.forms import UserCreationForm
from .forms import newUserForm, NewBusinessForm, NewCustomerForm, NewHomeForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.generic import ListView
from django.db.models import Q

# Create your views here.

class SearchResultsView(ListView):
    model = models.Product
    template_name = 'store/search.html'
    context_object_name = 'products'


    def get(self, request, *args, **kwargs):
        data = cartData(request)
        cartItems = data['cartItems']
        query = self.request.GET.get('search')
        products = models.Product.objects.filter(Q(name__icontains=query))
        context = {'products': products, 'cartItems': cartItems}
        return render(request, 'store/search.html', context=context)


def register_manager(request):
    form = newUserForm()
    if request.method == 'POST':
        form = newUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            manager = models.Manager.objects.create(
                user=user,
                email=form.cleaned_data['email'],
                name=form.cleaned_data['username']
            )
            manager.save()
            return redirect('login')
    context = {'form': form}
    return render(request, 'store/manager_register.html', context)


def login_manager(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('manager_store')
        else:
            messages.info(request, 'Please enter valid details')

    context = {}
    return render(request, 'store/manager_login.html', context)


def manager_store(request):
    if request.user.is_authenticated:
        manager = get_object_or_404(models.Manager, user=request.user)
        store = get_object_or_404(models.Store, manager=manager)
        products = models.Product.objects.filter(store=store)
        context = {'products': products}
        return render(request, 'store/manager_store.html', context)
    context = {'products': products}
    return render(request, 'store/manager_store.html', context)


# def register_user(request):
#     form = newUserForm()
#     if request.method == 'POST':
#         form = newUserForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             customer = models.Customer.objects.create(
#                 user=user,
#                 email=form.cleaned_data['email'],
#                 name=form.cleaned_data['username']
#             )
#             customer.save()
#             return redirect('login')

#     context = {'form': form}
#     return render(request, 'store/register.html', context)


def register_user(request):
    userForm = newUserForm()
    customerForm = NewCustomerForm()
    homeForm = NewHomeForm()
    businessForm = NewBusinessForm()

    if request.method == 'POST':
        print(request.POST)
        # userForm = newUserForm(request.POST)
        # print(userForm, "CLEANED")
        print(request.POST['password1'])
        userForm = newUserForm({
            'username': request.POST['username'],
            'email': request.POST['email'],
            'password1': request.POST['password1']
        })
        customerForm = NewCustomerForm({'kind': request.POST['kind']})
        print('user', userForm.error_messages)
        if customerForm.is_valid():
            print('customer')
        if not userForm.is_valid():
            print('user', userForm.error_messages)

        if userForm.is_valid() and customerForm.is_valid():
            print('valid')
            user = userForm.save()
            cleaned_form = userForm.cleaned_data
            customer = models.Customer.objects.create(
                user=user,
                email=cleaned_form['email'],
                name=cleaned_form['username'],
                kind=customerForm.cleaned_data['kind']
            )
            if customerForm.cleaned_data['kind'] == 'Home':
                homeForm = NewHomeForm({
                    "marriage_status": request.POST['marriage_status'],
                    "gender": request.POST['gender'],
                    "age": request.POST['age'],
                    "income": request.POST['income']
                })
                if homeForm.is_valid():
                    home = models.Home.objects.create(
                        marriage_status=homeForm.cleaned_data['marriage_status'],
                        gender=homeForm.cleaned_data['gender'],
                        age=int(homeForm.cleaned_data['age']),
                        income=float(homeForm.cleaned_data['income'])
                    )
                    home.save()
                    customer.home_customer = home
                else:
                    messages.info(request, 'Please enter valid details')
            else:
                businessForm = NewBusinessForm({
                    "business_category": request.POST['business_category'],
                    "gross_annual_income": request.POST['gross_annual_income']
                })
                if businessForm.is_valid():
                    business = models.Business.objects.create(
                        business_category=businessForm.cleaned_data['business_category'],
                        gross_annual_income=businessForm.cleaned_data['gross_annual_income']
                    )
                    business.save()
                    customer.business_customer = business
                else:
                    messages.info(request, 'Please enter valid details')
            customer.save()
            return redirect('login')
        else:
            print('invalid')
            messages.info(request, 'Please enter valid details')

    context = {'userForm': userForm, 'customerForm': customerForm, 'homeForm': homeForm, 'businessForm': businessForm}
    return render(request, 'store/register.html', context)


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            messages.info(request, 'Please enter valid details')

    context = {}
    return render(request, 'store/login.html', context)


def logout_user(request):
    logout(request)
    return redirect("store")

from django.db.models import Sum, F, FloatField, Count


def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    total_customers = 0
    total_sales = models.OrderItem.objects.aggregate(total_sales=Sum(F('quantity') * F('product__price'), output_field=FloatField()))
    total_customers = models.Customer.objects.count()
    top_categories = models.Product.objects.values('category').annotate(product_count=Count('id')).order_by('-product_count')[:5]
    top_businesses = models.Business.objects.annotate(product_count=Count('customer__order__orderitem__product')).order_by('-product_count')[:5]
    print("Biss: ", top_businesses)
    products = models.Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


# Aggregate Sales

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def update_item(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = models.Product.objects.get(id=productId)
    # order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
    # orderItem, created = models.OrderItem.objects.get_or_create(order=order, product=product)

    # if action == 'add':
    #     orderItem.quantity += 1
    # elif action == 'remove':
    #     orderItem.quantity -= 1
    # orderItem.save()
    # if orderItem.quantity <= 0:
    #     orderItem.delete()
    # return JsonResponse('Item was added', safe=False)
    order, created = models.Order.objects.get_or_create(
                customer=customer, complete=False)
    if action == 'add':
        if product.stock > 0:  # Check if there is available stock
            if order.orderitem_set.exists() and order.orderitem_set.first().product.store != product.store:
                return JsonResponse(
                    'Cannot mix products from different stores in the same cart',
                    safe=False)
            orderItem, created = models.OrderItem.objects.get_or_create(
                order=order, product=product)
            orderItem.quantity += 1
            orderItem.save()
            product.stock -= 1  # Reduce the stock by 1
            product.save()
            return JsonResponse('Item was added', safe=False)
        else:
            return JsonResponse('Out of stock', safe=False)
    elif action == 'remove':
        orderItem = models.OrderItem.objects.get(order=order)
        orderItem.quantity -= 1
        orderItem.save()
        if orderItem.quantity <= 0:
            orderItem.delete()
        product.stock += 1  # Increase the stock by 1
        product.save()
        return JsonResponse('Item was removed', safe=False)

from django.views.decorators.csrf import csrf_exempt
import random

@csrf_exempt

def orderProcess(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = models.Order.objects.get_or_create(customer=customer, complete=False)

    else:
        print('User is not logged in')
        print('COOKIES:', request.COOKIES)
        name = data['form']['name']
        email = data['form']['email']

        cookieData = cookieCart(request)
        items = cookieData['items']

        customer, created = models.Customer.objects.get_or_create(
            email=email,
        )
        customer.name = name
        customer.save()

        order = models.Order.objects.create(
            customer=customer,
            complete=False
        )

        for item in items:
            product = models.Product.objects.get(id=item['product']['id'])
            orderItem = models.OrderItem.objects.create(
                product=product,
                order=order,
                quantity=item['quantity']
            )

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    curr_store = order.orderitem_set.first().product.store
    order.salesperson_assigned = random.choice(models.SalesPersons.objects.filter(store_assigned=curr_store))

    if total == float(order.cart_total):
        order.complete = True
    order.save()

    if order.shipping is True:
        models.ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            contact=data['shipping']['contact'],
            state=data['shipping']['state'],
            city=data['shipping']['city'],
            zipcode=data['shipping']['zipcode']
        )

    return JsonResponse('Payment Complete', safe=False)


def orderHistory(request):
    orders = []
    if request.user.is_authenticated:
        customer = get_object_or_404(models.Customer, user=request.user)

        orders = models.Order.objects.filter(customer=customer, complete=True)
        for order in orders:
            order.order_items = order.orderitem_set.all()
    context = {'orders': orders}
    return render(request, 'store/history.html', context)

