from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, related_name='restaurants', on_delete=models.CASCADE)
    address = models.CharField(max_length=1024)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='menus', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} - {self.restaurant.name}'


class Meal(models.Model):
    menu = models.ForeignKey(Menu, related_name='meals', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='meals', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    image = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} - {self.menu.name}'


class Cart(models.Model):
    user = models.ForeignKey(User, related_name='cart', on_delete=models.CASCADE)
    meals = models.ManyToManyField(Meal, through='CartMeal')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Cart - {self.user.username}'


class CartMeal(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.meal.name}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
        ('owner', 'Owner'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    store_address = models.CharField(max_length=255, blank=True, null=True)
    floor = models.CharField(max_length=255, blank=True, null=True)
    store_name = models.CharField(max_length=255, blank=True, null=True)
    brand_name = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username}'s Profile"
