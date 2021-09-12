from django.urls import path
from . import views

app_name = 'messenger'
urlpatterns = [
    path('', views.messenger, name="messenger"),
    path('chat/<chat>', views.show_chat, name="show_chat"),
    path('chatting/1', views.send_message, name="send_message"),
    path('upload', views.upload, name="upload"),
    path('recognition', views.recognition, name="recognition"),
    path('accounts/edit', views.edit_user, name="edit_user"),
    path('accounts/saved_<userID>', views.save_user, name="save_user"),
    path('new_chat', views.chat_create, name="chat_create"),
    path('chat/<chat>/edit', views.edit_chat, name="edit_chat"),
    path('chat_create_success', views.chat_create_success, name="chat_create_success"),
    path('chat/<chatID>/save', views.edit_chat_save, name="edit_chat_save"),
    path('chat/<chatID>/delete', views.chat_delete, name="chat_delete"),
    path('remove_user/<chat_id>/<user>', views.remove_user, name="remove_user"),
    path('add_chatUser/<chat_id>', views.add_chatUser, name="add_chatUser"),
]