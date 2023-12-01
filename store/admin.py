from django.contrib import admin
from .models import Customer, Product, Order, OrderItem, ShippingAddress, Region, Store, SalesPersons, Home, Business

# Register your models here.
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Store, Product

class CustomUserAdmin(UserAdmin):
    def has_module_permission(self, request):
        # Check if the user is a manager of any store
        if request.user.is_authenticated:
            return Store.objects.filter(manager=request.user).exists()
        return False

# Register the CustomUserAdmin for the User model
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class StoreAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Filter the queryset based on the currently logged-in user as a manager
        if request.user.is_authenticated:
            return qs.filter(manager=request.user)
        return qs

# Register the StoreAdmin for the Store model
admin.site.register(Store, StoreAdmin)

class ProductAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Filter the queryset based on the currently logged-in user's assigned store
        if request.user.is_authenticated:
            assigned_store = Store.objects.filter(manager=request.user).first()
            if assigned_store:
                return qs.filter(store=assigned_store)
        return qs

# Register the ProductAdmin for the Product model
admin.site.register(Product, ProductAdmin)


admin.site.register(Customer)
# admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Region)
# admin.site.register(Store)
admin.site.register(SalesPersons)
admin.site.register(Home)
admin.site.register(Business)
