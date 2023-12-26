from django.utils.http import urlsafe_base64_encode
from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required

#Account Activation
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


 
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.http import HttpResponse

from carts.views import _cart_id
from carts.models import Cart, CartItem


User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name   = form.cleaned_data['first_name']
            last_name    = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email        = form.cleaned_data['email']
            password     = form.cleaned_data['password']
            username     = email.split('@')[0]
            
            user         = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()
            # user Activation
            current_site = get_current_site(request)
            mail_subject = "Pleass Activate your Account"
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Registration successful.')
            return redirect('register')
        else:

            form = RegistrationForm()
    else:

        form = RegistrationForm()

    context = {'form': form}
    return render(request, 'accounts/register.html', context)


def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            # التحقق من البريد الإلكتروني بشكل مباشر
            user = User.objects.get(email=email)
            
            # مصادقة المستخدم
            if user.check_password(password):
                # في حالة نجاح المصادقة، قم بتسجيل الدخول
                try:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    existing_cart_items = CartItem.objects.filter(cart=cart)
                    if existing_cart_items:
                        cart_item = CartItem.objects.filter(cart=cart)

                        for item in cart_item:
                            item.user = user
                            item.save()
                except:
                    pass
                login(request, user)
                messages.success(request, 'Login is Successful')
                return redirect('dashboard')
            else:
                # في حالة فشل المصادقة، أظهر رسالة خطأ
                messages.error(request, 'ERROR: Failed to Register Permission')
                return redirect('user_login')

        except User.DoesNotExist:
            # إذا لم يتم العثور على المستخدم
            messages.error(request, 'ERROR: User Not Found ')
            return redirect('user_login')

    return render(request, 'accounts/user_login.html')


@login_required(login_url = 'user_login')
def user_logout(request):
    auth.logout(request)
    messages.success(request, 'You Are Logged out')
    return redirect('user_login')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return HttpResponse("Account activated successfully!")
        else:
            return HttpResponse("Activation link is invalid!")
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):

        return HttpResponse("Activation link is invalid!")


@login_required(login_url = 'user_login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # reser password
            current_site = get_current_site(request)
            mail_subject = "Reset your Password"
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            message.success(request, 'Password reset email has sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')


def resetpassword_valldate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            # عملية إعادة تعيين كلمة المرور
            new_password = "your_new_password_here"  # يجب تغييرها إلى كلمة مرور جديدة
            user.set_password(new_password)
            user.save()
            
            messages.success(request, 'Password reset successful.')
            return redirect('user_login')
        else:
            messages.error(request, 'Invalid token for password reset.')
            return redirect('forgotPassword')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'Invalid link for password reset.')
        return redirect('forgotPassword')
