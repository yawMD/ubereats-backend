from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import CreateUserView, LoginView, CategoryViewSet, meals_by_restaurant, meals_by_category, \
    restaurants_by_category

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'restaurants', views.RestaurantViewSet)
router.register(r'menus', views.MenuViewSet)
router.register(r'meals', views.MealViewSet)
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'cartmeals', views.CartMealViewSet, basename='cartmeal')
router.register(r'categories', CategoryViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    path('register/', CreateUserView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('meals/restaurant/<int:restaurant_id>/', meals_by_restaurant, name='meals-by-restaurant'),
    path('meals/category/<int:category_id>/', meals_by_category, name='meals-by-category'),
    path('restaurants/category/<int:category_id>/', restaurants_by_category, name='restaurants-by-category'),

]
