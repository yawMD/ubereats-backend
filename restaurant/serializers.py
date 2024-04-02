from rest_framework import serializers
from .models import Restaurant, Menu, Meal, Cart, CartMeal, Profile, Category
from django.contrib.auth.models import User


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class MenuSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.ReadOnlyField(source='restaurant.name')

    class Meta:
        model = Menu
        fields = ['id', 'name', 'description', 'restaurant', 'restaurant_name', 'image']
        extra_kwargs = {
            'restaurant': {'write_only': True},
        }


class MealSerializer(serializers.ModelSerializer):
    category_details = CategorySerializer(source='category', read_only=True)
    menu_name = serializers.ReadOnlyField(source='menu.name')

    class Meta:
        model = Meal
        fields = ['id', 'name', 'description', 'price', 'menu', 'menu_name', 'image', 'category', 'category_details']
        extra_kwargs = {
            'menu': {'write_only': True},
        }


class CartMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartMeal
        fields = ['id', 'cart', 'meal', 'quantity']
        extra_kwargs = {
            'cart': {'write_only': True},
            'meal': {'write_only': True}
        }


class CartSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')  # Assuming you want to include the user's ID

    class Meta:
        model = Cart
        fields = ['id', 'user', 'meals', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Assume the cart is related to the request's user
        user = self.context['request'].user
        cart = Cart.objects.create(user=user)
        return cart


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='profile.role', read_only=True, label='Role')
    role = serializers.CharField(write_only=True, required=False, default='user')
    password = serializers.CharField(write_only=True)
    store_address = serializers.CharField(source='profile.store_address', write_only=True, required=False,
                                          allow_blank=True, allow_null=True)
    floor = serializers.CharField(source='profile.floor', write_only=True, required=False, allow_null=True)
    store_name = serializers.CharField(source='profile.store_name', write_only=True, required=False, allow_blank=True,
                                       allow_null=True)
    brand_name = serializers.CharField(source='profile.brand_name', write_only=True, required=False, allow_blank=True,
                                       allow_null=True)
    first_name = serializers.CharField(source='profile.first_name', write_only=True, required=True, allow_blank=True,
                                       allow_null=True)
    last_name = serializers.CharField(source='profile.last_name', write_only=True, required=True, allow_blank=True,
                                      allow_null=True)
    location = serializers.CharField(source='profile.location', write_only=True, required=False, allow_blank=True,
                                     allow_null=True)

    store_address_display = serializers.CharField(source='profile.store_address', read_only=True)
    floor_display = serializers.CharField(source='profile.floor', read_only=True)
    store_name_display = serializers.CharField(source='profile.store_name', read_only=True)
    brand_name_display = serializers.CharField(source='profile.brand_name', read_only=True)
    first_name_display = serializers.CharField(source='profile.first_name', read_only=True)
    last_name_display = serializers.CharField(source='profile.last_name', read_only=True)
    location_display = serializers.CharField(source='profile.location', read_only=True)

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})  # Extract profile-related data

        role = validated_data.pop('role', 'user')

        # Create the user
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', '')
        )
        user.set_password(validated_data['password'])
        user.save()

        profile_data['role'] = role
        # Create or update the user's profile with the extracted data
        Profile.objects.update_or_create(user=user, defaults=profile_data)
        user.refresh_from_db()

        # Check if the fields for creating a restaurant are provided
        store_address = profile_data.get('store_address')
        floor = profile_data.get('floor')
        store_name = profile_data.get('store_name')
        brand_name = profile_data.get('brand_name')
        location = profile_data.get('location')

        if store_address and store_name:
            # Create a new restaurant instance
            Restaurant.objects.create(
                name=store_name,
                owner=user,
                address=f"{store_address}, Floor: {floor}" if floor else store_address,
                description=f"Brand: {brand_name}, Location: {location}" if brand_name or location else "",
                # You might want to handle the 'image' field as well, if applicable
            )

        return user

    def to_representation(self, instance):
        """ Modify the representation of the serializer data. """
        ret = super().to_representation(instance)
        profile = instance.profile
        ret['store_address_display'] = profile.store_address
        ret['floor_display'] = profile.floor
        ret['store_name_display'] = profile.store_name
        ret['brand_name_display'] = profile.brand_name
        ret['first_name_display'] = profile.first_name
        ret['last_name_display'] = profile.last_name
        ret['location_display'] = profile.location

        # Attempt to fetch the restaurant associated with the user
        try:
            restaurant = Restaurant.objects.get(owner=instance)
            # If you have a RestaurantSerializer, you can use it to serialize the restaurant data
            restaurant_data = {
                'id': restaurant.id,
                'name': restaurant.name,
                'address': restaurant.address,
                'description': restaurant.description,
                'image': restaurant.image
                # Include other fields as needed
            }
        except Restaurant.DoesNotExist:
            restaurant_data = None

        # Add the restaurant data to the response
        ret['restaurant'] = restaurant_data
        return ret

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'role', 'role_display', 'store_address', 'floor', 'store_name',
                  'brand_name', 'location', 'first_name', 'last_name', 'store_name_display', 'store_address_display',
                  'floor_display', 'brand_name_display', 'location_display', 'first_name_display', 'last_name_display')
