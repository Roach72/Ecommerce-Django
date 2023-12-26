from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
        print("New cart created:", cart)
    return cart

@login_required(login_url='user_login')
def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                Key = item
                value = request.POST[Key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=Key, variation_value__iexact=value)
                    product_variation.append(variation)
                except Variation.DoesNotExist:
                    pass

            existing_cart_items = CartItem.objects.filter(user=current_user, product=product)
            if existing_cart_items.exists():
                matching_products = CartItem.objects.filter(user=current_user, product=product)
                for cart_item in matching_products:
                    matching_variations = cart_item.variations.all()
                    if all(variation in matching_variations for variation in product_variation):
                        cart_item.quantity += 1
                        cart_item.save()
                        return redirect('carts')

            cart_item = CartItem.objects.create(product=product, quantity=1, user=current_user)
            for item in product_variation:
                cart_item.variations.add(item)
            cart_item.save()

            return redirect('carts')

        return redirect('carts')

    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                Key = item
                value = request.POST[Key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=Key, variation_value__iexact=value)
                    product_variation.append(variation)
                except Variation.DoesNotExist:
                    pass

            cart_id = _cart_id(request)
            cart, created = Cart.objects.get_or_create(cart_id=cart_id)
            

            existing_cart_items = CartItem.objects.filter(cart=cart, product=product)
            if existing_cart_items.exists():
                matching_products = CartItem.objects.filter(cart=cart, product=product)
                for cart_item in matching_products:
                    matching_variations = cart_item.variations.all()
                    # التأكد من توافق المتغيرات للمنتجات وزيادة الكمية إن وجد توافق
                    if all(variation in matching_variations for variation in product_variation):
                        cart_item.quantity += 1
                        cart_item.save()
                        return redirect('carts')

            # إذا لم يكن هناك توافق في المنتجات، أنشئ عنصرًا جديدًا في السلة
            cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            for item in product_variation:
                cart_item.variations.add(item)
            cart_item.save()

            return redirect('carts')

        return redirect('carts')  # يجب أن يتم توجيه المستخدم لعرض السلة بعد الانتهاء من عمليات الإضاف



def remove_cart(request, product_id):
    # هذا الكود به خطا الان مكانه ااساسي اسف واللذي اسفل هنا 
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(product=product, user=request.user)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(product=product, cart=cart)
    cart_items.delete()
    return redirect('carts')

def remove_cart_item(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(product=product, user=request.user)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(product=product, cart=cart)

    if cart_items.exists():
        cart_items = cart_items.first()  # اختر أول عنصر أو طور الخوارزمية بحسب ما تحتاج
        if cart_items.quantity > 1:
            cart_items.quantity -= 1
            cart_items.save()
        else:
            cart_items.delete()
    return redirect('carts')

def carts(request, total=0, quantity=0, cart_item=None):
    cart_items = []
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for item in cart_items:  # تغيير اسم المتغير هنا
            total += (item.product.price * item.quantity)
            quantity += item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass 
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
    }
    return render(request, 'store/carts.html', context)

@login_required(login_url='user_login')
def checkout(request, total=0, quantity=0, cart_item=None):
    cart_items = []
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for item in cart_items:  # تغيير اسم المتغير هنا
            total += (item.product.price * item.quantity)
            quantity += item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass 
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
    }
    return render(request, 'store/checkout.html', context)