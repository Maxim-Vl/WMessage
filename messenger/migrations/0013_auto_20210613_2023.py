# Generated by Django 3.2 on 2021-06-13 17:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0012_alter_chat_moderator_moderator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat_moderator',
            name='moderator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='chat_user',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats', to=settings.AUTH_USER_MODEL),
        ),
    ]
