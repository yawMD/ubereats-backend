Examples:
Below are the CRUD (Create, Read, Update, Delete) operations and other operations defined in your Django Rest Framework (DRF) code. Each view or viewset is formatted as per Python and DRF conventions:

### `RestaurantViewSet`:

- **Create** a Restaurant: Handled by `ModelViewSet`'s `create` method.
- **Read** Restaurant list and details: Handled by `ModelViewSet`'s `list` and `retrieve` methods.
- **Update** a Restaurant: Handled by `ModelViewSet`'s `update` and `partial_update` methods.
- **Delete** a Restaurant: Handled by `ModelViewSet`'s `destroy` method.

```python
class RestaurantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Restaurant.objects.all().select_related('owner').defer('description', 'created_at', 'updated_at')
    serializer_class = RestaurantSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().annotate(number_of_menus=Count('menus'))
        page = self.paginate_queryset(queryset)
        if page is not included:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

```

### `MenuViewSet`:

- **Create** a Menu
- **Read** Menu list and details
- **Update** a Menu
- **Delete** a Menu

```python
class MenuViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Menu.objects.all().select_related('restaurant').prefetch_related('meals').defer('description', 'created_at', 'updated_at')
    serializer_class = MenuSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrAdmin]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

```

### `MealViewSet`:

- **Create** a Meal
- **Read** Meal list and details
- **Update** a Meal
- **Delete** a Meal

```python
class MealViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Meal.objects.all().select_related('menu').defer('description', 'created_at', 'updated_at')
    serializer_class = MealSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrAdmin]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

```

### `CartViewSet`:

- **Read** Cart details: Custom `get_queryset` method.

```python
class CartViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Cart.objects.filter(user=user).prefetch_related(
            Prefetch('cartmeals', queryset=CartMeal.objects.select_related('meal'))
        )
        return queryset
```

### `CartMealViewSet`:

- **Create** a CartMeal
- **Read** CartMeal list and details
- **Update** a CartMeal
- **Delete** a CartMeal

```python
class CartMealViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CartMeal.objects.all().select_related('cart', 'meal').defer('created_at', 'updated_at')
    serializer_class = CartMealSerializer

    def get_permissions(self):
        return [IsAdminUser()] if self.action != 'create' else [IsAuthenticated()]

    def perform_create(self, serializer):
        if self.request.user.is_staff or serializer.validated_data['cart'].user == self.request.user:
            serializer.save()
        else:
            raise PermissionDenied('You do not have permission to add items to this cart.')

```

### `CreateUserView`:

- **Create** a User

```python
class CreateUserView(generics.CreateAPIView):
    permission_classes = []
    serializer_class = UserSerializer

```

### `LoginView`:

- **Login**: Authenticates a user and returns a token.

```python
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        # Login logic

```

Each class corresponds to a set of operations that can be performed on the respective model. The `get_permissions` method customizes the permissions based on the action being performed, ensuring that only authorized users can create, update, or delete entries.

### `Meals_by_category`:

```jsx
@api_view(['GET'])
def meals_by_category(request, category_id):
    # Get all categories with a count of meals in each category
    categories_with_meal_count = Category.objects.annotate(meal_count=Count('meal'))

    # Get the specific category with the provided category_id
    category = categories_with_meal_count.get(id=category_id)

    # Serialize the category data
    serializer = CategorySerializer(category)

    # Return the category data along with the meal count
    return Response(serializer.data)
```

### `restaurants_by_category`:

```jsx
@api_view(['GET'])
def restaurants_by_category(request, category_id):
    # Prefetch the related Menu and Meal objects to reduce the number of database queries
    meals = Meal.objects.filter(category_id=category_id).select_related('menu').only('menu__restaurant')
    menus = Menu.objects.prefetch_related(Prefetch('meals', queryset=meals, to_attr='filtered_meals'))

    # Filter restaurants based on the prefetched Menus that have Meals in the specified category
    restaurants = Restaurant.objects.prefetch_related(Prefetch('menus', queryset=menus, to_attr='filtered_menus')).filter(menus__filtered_meals__isnull=False).distinct()

    serializer = RestaurantSerializer(restaurants, many=True)
    return Response(serializer.data)
```

### `meals_by_restaurant`:

```jsx
@api_view(['GET'])
def meals_by_restaurant(request, restaurant_id):
    # Use select_related to fetch related Menu objects in a single query
    meals = Meal.objects.filter(menu__restaurant_id=restaurant_id).select_related('menu')

    serializer = MealSerializer(meals, many=True)
    return Response(serializer.data)
```


1. Register User

    Endpoint Name: Register
    HTTP Method: POST
    URL: /register/
    Headers: Content-Type: application/json
    Permissions: Open access
    Request Body:



    {
      "username": "newuser",
      "password": "newpassword",
      "email": "newuser@example.com",
      "role": "user"
    }

2. Login

    Endpoint Name: Login
    HTTP Method: POST
    URL: /login/
    Headers: Content-Type: application/json
    Permissions: Open access
    Request Body:



            {
              "username": "existinguser",
              "password": "userpassword"
            }

3. Create Cart

    Endpoint Name: Create Cart
    HTTP Method: POST
    ```URL: /cart/```
    ```Headers: Content-Type: application/json, Authorization: Token <user_token>```
   Permissions: Authenticated users only


   4. Add Meal to Cart (CartMeal)
       Endpoint Name: Add Meal to Cart
       HTTP Method: POST
      ``` URL: /cartmeals/```
       Headers: Content-Type: application/json, Authorization: Token <user_token>
       Permissions: Authenticated users, cart owner only

Request Body:


       {
         "cart": 1,
         "meal": 2,
         "quantity": 3
       }


5. List All Restaurants

    Endpoint Name: List Restaurants
    HTTP Method: GET
   ``` URL: /restaurants/```
    Headers: Authorization: Token <user_token> (optional, if authentication is required)
    Permissions: Open access or authenticated users only, based on your configuration
    Request Body: None

6. Retrieve Restaurant Details

    Endpoint Name: Get Restaurant Details
    HTTP Method: GET

    ```URL: /restaurants/{restaurant_id}/```
    Headers: Authorization: Token <user_token> (optional, if authentication is required)
    Permissions: Open access or authenticated users only, based on your configuration
    Request Body: None


7. Create Restaurant (Admins only)

    Endpoint Name: Create Restaurant
    HTTP Method: POST
  ```  URL: /restaurants/```
    Headers: Content-Type: application/json, Authorization: Token <admin_token>
    Permissions: Admins only
    Request Body:



    {
      "name": "The Green Terrace",
      "address": "123 Elm Street",
      "description": "A cozy place with a wide selection of vegetarian dishes."
    }



8. Update CartMeal Quantity

    Endpoint Name: Update CartMeal Quantity
    HTTP Method: PATCH
    ``URL: /cartmeals/{cartmeal_id}/``
    Headers: Content-Type: application/json, Authorization: Token <user_token>
    Permissions: Authenticated users, cart owner only
    Request Body:



    {
      "quantity": 2
    }


9. Delete CartMeal

    Endpoint Name: Remove Meal from Cart
    HTTP Method: DELETE
    ```URL: /cartmeals/{cartmeal_id}/```
    Headers: Authorization: Token <user_token>
    Permissions: Authenticated users, cart owner only
    Request Body: None


10. List User's Cart Items

    Endpoint Name: List Cart Items
    HTTP Method: GET
   ``` URL: /cart/```
    Headers: Authorization: Token <user_token>
    Permissions: Authenticated users only
    Request Body: None
