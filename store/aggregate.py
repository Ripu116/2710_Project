from .models import OrderItem, Customer
from django.db.models import Sum, F

total_customers = 0
total_sales = OrderItem.objects.aggregate(total_sales=Sum(F('quantity') * F('product__price')))
total_customers = Customer.objects.count()
print(total_customers)
