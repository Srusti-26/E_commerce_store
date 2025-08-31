from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Category, Product, Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm
import json

def product_list(request, category_slug=None):
    """Display a list of available products, optionally filtered by category."""
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            name__icontains=search_query
        ) | products.filter(
            description__icontains=search_query
        )
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created')
    else:
        products = products.order_by('name')
    
    return render(request, 'store/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'search_query': search_query,
        'sort_by': sort_by
    })

def product_detail(request, slug):
    """Display detailed information about a specific product."""
    product = get_object_or_404(Product, slug=slug, available=True)
    
    # Get related products from the same category
    related_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(id=product.id)[:4]
    
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products
    })

def get_or_create_cart(request):
    """Helper function to get the current user's cart or create a new one."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        # Merge session cart if exists
        session_cart_id = request.session.get('cart_id')
        if session_cart_id and created:
            try:
                session_cart = Cart.objects.get(id=session_cart_id, user=None)
                # Move items from session cart to user cart
                for item in session_cart.items.all():
                    try:
                        existing_item = CartItem.objects.get(cart=cart, product=item.product)
                        existing_item.quantity += item.quantity
                        existing_item.save()
                    except CartItem.DoesNotExist:
                        item.cart = cart
                        item.save()
                session_cart.delete()
                del request.session['cart_id']
            except Cart.DoesNotExist:
                pass
    else:
        # For anonymous users, use session-based cart
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id, user=None)
            except Cart.DoesNotExist:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    
    return cart

@require_POST
def cart_add(request, product_id):
    """Add a product to the shopping cart."""
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    quantity = int(request.POST.get('quantity', 1))
    
    # Check if the product is already in the cart
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.quantity += quantity
        cart_item.save()
    except CartItem.DoesNotExist:
        CartItem.objects.create(cart=cart, product=product, quantity=quantity)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_count = sum(item.quantity for item in cart.items.all())
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to your cart.',
            'cart_count': cart_count,
            'cart_total': float(cart.get_total_cost())
        })
    
    messages.success(request, f'{product.name} added to your cart.')
    return redirect('store:cart_detail')

def cart_remove(request, product_id):
    """Remove a product from the shopping cart."""
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart_count = sum(item.quantity for item in cart.items.all())
            return JsonResponse({
                'success': True,
                'message': f'Removed {product.name} from your cart.',
                'cart_count': cart_count,
                'cart_total': float(cart.get_total_cost())
            })
        
        messages.success(request, f'Removed {product.name} from your cart.')
    except CartItem.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Item not found in cart.'})
    
    return redirect('store:cart_detail')

def cart_detail(request):
    """Display the contents of the shopping cart."""
    cart = get_or_create_cart(request)
    return render(request, 'store/cart_detail.html', {'cart': cart})

@login_required
@login_required
def checkout(request):
    """Process the checkout and create an order."""
    cart = get_or_create_cart(request)
    
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('store:cart_detail')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Process the order
            order = Order.objects.create(
                user=request.user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                address=form.cleaned_data['address'],
                postal_code=form.cleaned_data['postal_code'],
                city=form.cleaned_data['city']
            )
            
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                )
            
            # Clear the cart
            cart.items.all().delete()
            
            messages.success(request, 'Your order has been placed successfully!')
            return redirect('store:order_confirmation')
    else:
        form = CheckoutForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email
        })
    
    return render(request, 'store/checkout.html', {'cart': cart, 'form': form})

@login_required
def order_confirmation(request):
    """Display order confirmation page."""
    return render(request, 'store/order_confirmation.html')

# API Views
def api_products(request):
    """API endpoint for products."""
    products = Product.objects.filter(available=True)
    category_slug = request.GET.get('category')
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    products_data = [{
        'id': p.id,
        'name': p.name,
        'slug': p.slug,
        'price': float(p.price),
        'description': p.description,
        'image': p.image.url if p.image else None,
        'category': p.category.name
    } for p in products]
    
    return JsonResponse({
        'products': products_data,
        'total': products.count()
    })

def api_cart_status(request):
    """API endpoint for cart status."""
    cart = get_or_create_cart(request)
    cart_items = [{
        'id': item.id,
        'product_name': item.product.name,
        'product_price': float(item.product.price),
        'quantity': item.quantity,
        'total': float(item.get_cost())
    } for item in cart.items.all()]
    
    return JsonResponse({
        'cart_items': cart_items,
        'cart_count': sum(item.quantity for item in cart.items.all()),
        'cart_total': float(cart.get_total_cost())
    })

def about(request):
    """Display the about page."""
    return render(request, 'store/about.html')

def contact(request):
    """Display the contact page."""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Here you can add email sending logic or save to database
        # For now, we'll just show a success message
        messages.success(request, f'Thank you {name}! Your message has been sent successfully. We will get back to you soon.')
        return redirect('store:contact')
    
    return render(request, 'store/contact.html')