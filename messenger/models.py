import os
from django.db import models as m
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.dispatch import receiver


# Модель пользователя
class CustomUser(AbstractUser):
    image = m.ImageField(upload_to="img/", default='default_img.jpg')


# Модель "Тип чата"
class ChatType(m.Model):
    name = m.CharField('Тип чата', max_length=50)
    priority = m.PositiveIntegerField('Приоритет')

    def __str__(self):
        return self.name


# Модель "Чат"
class Chat(m.Model):
    name = m.CharField('Название', max_length=50)
    chat_type = m.ForeignKey(ChatType, on_delete=m.CASCADE, verbose_name='Тип чата')
    is_open = m.BooleanField('Общий', default=False)
    description = m.TextField('Описание', null=True)

    def calculateMessages(self):
        return Message.objects.filter(mto=self, read_status=1).count()

    unread = property(calculateMessages)

    def __str__(self):
        return self.name


# Модель "Пользователи чата"
class Chat_User(m.Model):
    chat = m.ForeignKey(Chat, on_delete=m.CASCADE, related_name="users")
    user = m.ForeignKey(CustomUser, on_delete=m.CASCADE, related_name="chats")
    is_moderator = m.BooleanField(default=False)

    class Meta:
        unique_together = ('chat', 'user',)

    def __str__(self):
        return str(self.chat) + '-' + str(self.user)


# Модель "Сообщение"
class Message(m.Model):
    mfrom = m.ForeignKey(CustomUser, on_delete=m.CASCADE, verbose_name='Отправитель')
    mto = m.ForeignKey(Chat, on_delete=m.CASCADE, verbose_name='Получатель')
    message_text = m.TextField('Сообщение', blank=False)
    is_audio = m.BooleanField('Голосовое сообщение', default=False)
    time = m.DateTimeField('Время отправления', default=now, editable=False)
    read_status = m.IntegerField('Статус')

    def __str__(self):
        return self.message_text


# Модель "Прикрепленный файл"
class MessageFiles(m.Model):
    message = m.ForeignKey(Message, on_delete=m.CASCADE, related_name='files')

    def get_upload_path(instance, filename):
        return os.path.join(
            "chat_%s" % instance.message.mto.name, filename)

    file = m.FileField(upload_to=get_upload_path)
    name = m.CharField('Имя файла', max_length=50, default='NoNameFile')

    def __str__(self):
        return str(self.file)

    def audiotypecheck(self):
        filename = self.file.name
        try:
            t = filename.split('.')[-1]
            if t == 'wav' or t == 'mp3':
                a = 1
            else:
                a = 0
        except Exception:
            a = -1
        return a


# Удаление файла изображени профиля при удалении пользователя
@receiver(m.signals.post_delete, sender=CustomUser)
def auto_delete_file_on_delete(sender, instance, **kwargs):

    if instance.image and not instance.image == "default_img.jpg":
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


# Удаление файла изображения профиля при изменении
@receiver(m.signals.pre_save, sender=CustomUser)
def auto_delete_file_on_change(sender, instance, **kwargs):

    if not instance.pk:
        return False

    try:
        old_file = CustomUser.objects.get(pk=instance.pk).image
    except CustomUser.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file and not old_file == "default_img.jpg":
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


# Удаление файла сообщения при удалении сообщения
@receiver(m.signals.post_delete, sender=MessageFiles)
def auto_delete_file_on_delete(sender, instance, **kwargs):

    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


# Удаление файла сообщения при изменении
@receiver(m.signals.pre_save, sender=MessageFiles)
def auto_delete_file_on_change(sender, instance, **kwargs):

    if not instance.pk:
        return False

    try:
        old_file = CustomUser.objects.get(pk=instance.pk).file
    except CustomUser.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)