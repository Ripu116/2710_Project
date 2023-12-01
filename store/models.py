from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Home(models.Model):
    MARRIAGE_STATUS_CHOICES = (
        ('single', 'Single'),
        ('married', 'Married'),
    )

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    marriage_status = models.CharField(max_length=10, choices=MARRIAGE_STATUS_CHOICES, default='')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='')
    age = models.IntegerField()
    income = models.DecimalField(max_digits=10, decimal_places=2)


class Business(models.Model):
    business_category = models.CharField(max_length=255)
    gross_annual_income = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.business_category


class Customer(models.Model):
    CUSTOMER_KIND_CHOICES = (
        ('home', 'Home'),
        ('business', 'Business'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    kind = models.CharField(max_length=10, choices=CUSTOMER_KIND_CHOICES, default='')
    business_customer = models.OneToOneField(Business, on_delete=models.CASCADE, null=True, blank=True)
    home_customer = models.OneToOneField(Home, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    manager = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class Store(models.Model):
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zipcode = models.IntegerField(max_length=100, null=True, blank=True)
    manager = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def totalSalesPersons(self):
        return SalesPersons.objects.filter(store_assigned=self).count()


class Product(models.Model):
    category_choices = (
        ("GROCERY", "Grocery"),
        ("ELECTRONIC", "Electronic"),
        ("CLOTHING", "Clothing"),
        ("FOOTWEAR", "Footwear"),
    )
    name = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=100, choices=category_choices, default='', null=True, blank=True)
    digital = models.BooleanField(default=False, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    stock = models.IntegerField(max_length=100, null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except (ValueError):
            url = ''
        return url


class SalesPersons(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    job_title = models.CharField(max_length=100, null=True, blank=True)
    salary = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zipcode = models.IntegerField(max_length=100, null=True, blank=True)
    store_assigned = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    complete = models.BooleanField(default=False, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    salesperson_assigned = models.ForeignKey(SalesPersons, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital is False:
                shipping = True
        return shipping

    @property
    def cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.total_price for item in orderitems])
        return total

    @property
    def cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    @property
    def total_price(self):
        # Possible None Error for self.product
        total = 0
        if self.product:
            total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    contact = models.IntegerField(max_length=30, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zipcode = models.IntegerField(max_length=100, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.address
