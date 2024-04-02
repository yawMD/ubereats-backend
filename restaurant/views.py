from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import Restaurant, Menu, Meal, Cart, CartMeal, Category
from .permissions import IsAdminUser, IsOwnerOrAdmin
from .serializers import RestaurantSerializer, MenuSerializer, MealSerializer, CartSerializer, CartMealSerializer, \
    CategorySerializer
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import UserSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework import status


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only admin users can perform create, update, and destroy actions.
            permission_classes = [IsAdminUser]
        else:
            # Any user can view the list and detail data (read-only actions).
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only admin and Owners  can perform create, update, and destroy actions.
            permission_classes = [IsOwnerOrAdmin]
        else:
            # Any user can view the list and detail data (read-only actions).
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


class MealViewSet(viewsets.ModelViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only admin and Owners  can perform create, update, and destroy actions.
            permission_classes = [IsOwnerOrAdmin]
        else:
            # Any user can view the list and detail data (read-only actions).
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.profile.role == 'admin':
            # Admin users get all carts
            return Cart.objects.all()
        else:
            # Regular users get only their cart
            return Cart.objects.filter(user=user)


class CartMealViewSet(viewsets.ModelViewSet):
    queryset = CartMeal.objects.all()
    serializer_class = CartMealSerializer

    def get_permissions(self):
        # This will return IsAuthenticated permission for every action.
        # If the action is not 'create', it will additionally require the user to be an admin.
        if self.action != 'create':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # Check if the cart belongs to the user or if the user is an admin
        if self.request.user.is_staff or serializer.validated_data['cart'].user == self.request.user:
            serializer.save()
        else:
            raise PermissionDenied('You do not have permission to add items to this cart.')


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only admin and Owners  can perform create, update, and destroy actions.
            permission_classes = [IsOwnerOrAdmin]
        else:
            # Any user can view the list and detail data (read-only actions).
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


class CreateUserView(generics.CreateAPIView):
    permission_classes = []
    serializer_class = UserSerializer


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            user_data = UserSerializer(user).data  # Serialize the user instance
            user_data['token'] = token.key  # Add the token to the serialized user data
            return Response(user_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def meals_by_restaurant(request, restaurant_id):
    meals = Meal.objects.filter(menu__restaurant_id=restaurant_id)
    serializer = MealSerializer(meals, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def meals_by_category(request, category_id):
    meals = Meal.objects.filter(category_id=category_id)
    serializer = MealSerializer(meals, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def restaurants_by_category(request, category_id):
    # Get restaurants that have meals in the specified category
    restaurant_ids = Meal.objects.filter(category_id=category_id).values_list('menu__restaurant', flat=True).distinct()
    restaurants = Restaurant.objects.filter(id__in=restaurant_ids)
    serializer = RestaurantSerializer(restaurants, many=True)
    return Response(serializer.data)
