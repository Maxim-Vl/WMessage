from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.db.models import Q
from django.views.generic import TemplateView, ListView
from django.views import generic
from .models import CustomUser, ChatType, Chat, Message, MessageFiles, Chat_User
from django.shortcuts import redirect
import speech_recognition as sr
from django.conf import settings


def countunread(request, chats):
    unread = {}
    if request.user.is_authenticated:
        for ch in chats:
            msg = Message.objects.filter(mto=ch, read_status=1)
            unread[ch]=msg.exclude(mfrom=request.user).count()
    else:
        for ch in chats:
            unread[ch]=0

    sorted_dict = {}
    sorted_keys = sorted(unread, key=unread.get, reverse=True)  # [1, 3, 2]

    for w in sorted_keys:
        sorted_dict[w] = unread[w]

    return sorted_dict


# Отображение начальной страницы
def messenger(request):
    users = CustomUser.objects.all()
    chat_types = ChatType.objects.all()
    if request.user.is_authenticated:
        chats = set(cchat.chat for cchat in request.user.chats.all()) | set(Chat.objects.filter(is_open=True))
    else:
        chats = set(Chat.objects.filter(is_open=True))

    messages = Message.objects.all()

    return render(request, "messenger/start_content.html", {
        "users": users,
        "chat_types": chat_types,
        "chats": chats,
        "messages": messages,
        "unread": countunread(request, chats),
    })


# Отображение чата
def show_chat(request, chat):
    users = CustomUser.objects.all()
    chat_types = ChatType.objects.all()
    if request.user.is_authenticated:
        chats = set(cchat.chat for cchat in request.user.chats.all()) | set(Chat.objects.filter(is_open=True))
    else:
        chats = set(Chat.objects.filter(is_open=True))

    messages = Message.objects.filter(mto=chat)

    if request.user.is_authenticated:
        msg = messages.exclude(mfrom=request.user)
        msg.update(read_status=0)


    cchat = Chat.objects.get(pk=chat)
    chat_users = set(cuser.user for cuser in cchat.users.all())
    moderators = set(cuser.user for cuser in cchat.users.filter(is_moderator=True))

    return render(request, "messenger/msg_list.html", {
        "users": users,
        "chat_types": chat_types,
        "chats": chats,
        "unread": countunread(request, chats),
        "messages": messages,
        "cchat": cchat,
        "chat_id": chat,
        "chat_users": chat_users,
        "moderators": moderators,
    })


# Отправка сообщения
def send_message(request):
    message_data = request.POST.get('text_input')
    chat_id = request.POST.get('chat_id')
    message = Message(
        mfrom=request.user,
        mto=Chat.objects.get(pk=chat_id),
        message_text=message_data,
        read_status=1
    )
    if not (message.message_text == Message.objects.latest('id').message_text or message.message_text == "") \
            or (message.message_text == "" and request.FILES.getlist('inputfiles')):
        message.save()

        files = request.FILES.getlist('inputfiles')
        for file in files:
            afile = MessageFiles(
                message=message,
                file=file,
                name=file.name
            )
            afile.save()

    return redirect('/chat/'+chat_id)

# Отправка голосового сообщения
def upload(request):
    audiofile = request.FILES.get('audio_data')

    chat_id = request.POST.get('cID')
    messenger(request)
    message = Message(
        mfrom=request.user,
        mto=Chat.objects.get(pk=chat_id),
        message_text="Голосовое сообщение",
        is_audio=True,
        read_status=1
    )
    message.save()

    afile = MessageFiles(
        message=message,
        name=audiofile.name
    )
    afile.file.save('file.wav', audiofile)
    afile.save()

    return HttpResponse('audio received')

def recognition(request):
    audiofileid = request.POST.get('audio_data')
    audiofile = MessageFiles.objects.get(id=audiofileid)
    r = sr.Recognizer()
    with sr.AudioFile(audiofile.file) as source:
        audio_data = r.record(source)
        try:
            text = r.recognize_google(audio_data, language="ru-RU")
            mtext = text
        except sr.UnknownValueError:
            mtext = "Не удалось распознать."
        except sr.RequestError as e:
            mtext = "Ошибка сервиса распознования"

    return HttpResponse(mtext)

# Удаление пользователя из чата
def remove_user(request, chat_id, user):
    chat_user = Chat_User.objects.get(chat=chat_id, user=user)
    chat_user.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


# Добавление пользователя в чат
def add_chatUser(request, chat_id,):
    chat = Chat.objects.get(id=chat_id)
    userslist = request.POST.getlist("addChatUsers")
    users = CustomUser.objects.filter(username__in=userslist)
    for user in users:
        chat_user = Chat_User.objects.create(
            chat=chat,
            user=user,
        )
        chat_user.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


# Отображение страницы редактирования пользователя
def edit_user(request):
    user = CustomUser.objects.get(pk=request.user.id)
    chat_types = ChatType.objects.all()
    if request.user.is_authenticated:
        chats = set(cchat.chat for cchat in request.user.chats.all()) | set(Chat.objects.filter(is_open=True))
    else:
        chats = set(Chat.objects.filter(is_open=True))
    messages = Message.objects.all()

    return render(request, "messenger/edit_user.html", {
        "user": user,
        "chat_types": chat_types,
        "chats": chats,
        "unread": countunread(request, chats),
        "messages": messages,
    })


# Сохранение данных пользователя в форме редактирования
def save_user(request, userID):
    username = request.POST.get('username')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    image = request.FILES.get('inputImage')

    user = CustomUser.objects.get(pk=userID)
    user.username = username
    user.first_name = first_name
    user.last_name = last_name
    user.image = image
    user.save()

    return redirect('/')


# Отображение формы создания чата
def chat_create(request):
    users = CustomUser.objects.all()
    chat_types = ChatType.objects.all()
    if request.user.is_authenticated:
        chats = set(cchat.chat for cchat in request.user.chats.all()) | set(Chat.objects.filter(is_open=True))
    else:
        chats = set(Chat.objects.filter(is_open=True))
    messages = Message.objects.all()

    return render(request, "messenger/chat_create.html", {
        "users": users,
        "chat_types": chat_types,
        "chats": chats,
        "unread": countunread(request, chats),
        "messages": messages,
    })


# Создание чата
def chat_create_success(request):
    chatname = request.POST.get("chatname")
    chattype = request.POST.get("chattype")
    chatdescription = request.POST.get("chatdescription")
    chatusers = request.POST.getlist("users")

    ct = ChatType.objects.filter(name=chattype).first()

    chat = Chat.objects.create(
        name=chatname,
        chat_type=ct,
        description=chatdescription,
    )
    chat.save()

    chat_user = Chat_User.objects.create(
        chat=chat,
        user=request.user,
    )
    chat_user.save()

    add_chat_users = CustomUser.objects.filter(username__in=chatusers)
    for chatuser in add_chat_users:
        chat_user = Chat_User.objects.create(
            chat=chat,
            user=chatuser,
        )
        chat_user.save()

    return redirect('/chat/' + str(chat.id))


# Отображение страницы редктирования чата
def edit_chat(request, chat):
    chat = Chat.objects.get(id=chat)
    users = CustomUser.objects.all()
    chat_types = ChatType.objects.all()
    if request.user.is_authenticated:
        chats = set(cchat.chat for cchat in request.user.chats.all()) | set(Chat.objects.filter(is_open=True))
    else:
        chats = set(Chat.objects.filter(is_open=True))
    chat_users = set(cuser.user for cuser in chat.users.all())
    moderators = set(cuser.user for cuser in chat.users.filter(is_moderator=True))

    return render(request, "messenger/chat_edit.html", {
        "chat": chat,
        "users": users,
        "chat_types": chat_types,
        "chats": chats,
        "unread": countunread(request, chats),
        "chat_users": chat_users,
        "moderators": moderators,
    })


# Сохранения чата после редактирования
def edit_chat_save(request, chatID):
    chatname = request.POST.get('chatname')
    chattype = ChatType.objects.get(name=request.POST.get('chattype'))
    chatdescription = request.POST.get('chatdescription')
    open = request.POST.get('openCheck', '') == 'on'

    chat = Chat.objects.get(pk=chatID)

    chat.name = chatname
    chat.chat_type = chattype
    chat.description = chatdescription
    chat.is_open = True if open else False

    chat.save()

    selected_users = request.POST.getlist('selected_users')
    Chat_User.objects.exclude(chat=chat, id__in=selected_users).update(
        is_moderator=False
    )
    Chat_User.objects.filter(chat=chat, id__in=selected_users).update(
        is_moderator=True
    )

    return redirect('/chat/' + chatID)


# Удаление чата
def chat_delete(request, chatID):
    chat = Chat.objects.get(pk=chatID)
    chat.delete()
    return redirect('/')