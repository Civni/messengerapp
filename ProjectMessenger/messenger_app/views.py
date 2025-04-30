from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import *
from django.contrib.auth.decorators import login_required
from .models import *
from django.db import transaction


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'profile_edit.html', {'form': form})


@login_required
def find_partner_view(request):
    user = request.user

    existing_chat = ChatRoom.objects.filter(user1=user).union(ChatRoom.objects.filter(user2=user)).first()
    if existing_chat:
        return redirect('chat', chat_id=existing_chat.id)

    if WaitingUser.objects.filter(user=user).exists():
        return render(request, 'chat/waiting.html')

    try:
        with transaction.atomic():
            waiting_user = WaitingUser.objects.exclude(user=user).order_by('joined_at').first()

            if waiting_user:
                chat = ChatRoom.objects.create(user1=waiting_user.user, user2=user)
                WaitingUser.objects.filter(user__in=[user, waiting_user.user]).delete()
                return redirect('chat', chat_id=chat.id)
            else:
                WaitingUser.objects.create(user=user)
                return render(request, 'chat/waiting.html')
    except Exception as e:
        print('Ошибка при поиске партнёра:', e)
        return redirect('profile')



@login_required
def chat_view(request, chat_id):
    WaitingUser.objects.filter(user=request.user).delete()
    chat = ChatRoom.objects.get(id=chat_id)

    if request.user == chat.user1:
        partner = chat.user2
    else:
        partner = chat.user1

    if request.user != chat.user1 and request.user != chat.user2:
        return redirect('profile')

    messages = Message.objects.filter(chat=chat).order_by('timestamp')

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = chat
            message.sender = request.user
            message.save()
            return redirect('chat', chat_id=chat.id)
    else:
        form = MessageForm()

    return render(request, 'chat/chat.html', {
        'chat': chat,
        'messages': messages,
        'form': form,
        'partner': partner,
    })


@login_required
def leave_chat_view(request, chat_id):
    chat = get_object_or_404(ChatRoom, id=chat_id)

    if request.user == chat.user1 or request.user == chat.user2:
        chat.delete()
    return redirect('find_partner')



@login_required
def check_chat_status(request):
    user = request.user
    chat = ChatRoom.objects.filter(user1=user).first() or ChatRoom.objects.filter(user2=user).first()
    if chat:
        return JsonResponse({'chat_id': chat.id})
    return JsonResponse({'chat_id': None})
