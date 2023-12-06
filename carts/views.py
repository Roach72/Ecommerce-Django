from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.

from django.db.models import F  # هنا نقوم باستيراد F()

# To add pro in cart page and get the id session
def _cart_id(request):
    cart =request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart



def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    
    if request.method == 'POST':
        for item in request.POST:
            Key = item
            value = request.POST[Key]

            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=Key, variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass

    cart = Cart.objects.get(cart_id=_cart_id(request))

    existing_cart_items = CartItem.objects.filter(cart=cart, product=product)
    if existing_cart_items.exists():
        matching_products = CartItem.objects.filter(cart=cart, product=product)
        for cart_item in matching_products:
            matching_variations = cart_item.variations.all()
            # التأكد من توافق اللون والمقاسات
            if all(variation in matching_variations for variation in product_variation):
                cart_item.quantity += 1
                cart_item.save()
                return redirect('carts')

    # إذا لم يكن هناك منتج متطابق، قم بإنشاء واحد جديد
    cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
    for item in product_variation:
        cart_item.variations.add(item)
    cart_item.save()

    return redirect('carts')



def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('carts')

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_items = CartItem.objects.filter(product=product, cart=cart)
    
    if cart_items.exists():
        cart_item = cart_items.first()
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('carts')


def carts(request, total=0, quantity=0, cart_item=None):
    cart_items = []
    try:
        tax = 0
        grand_total = 0
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