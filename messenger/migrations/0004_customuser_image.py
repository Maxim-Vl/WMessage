# Generated by Django 3.2 on 2021-05-24 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0003_alter_message_read_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='image',
            field=models.ImageField(default='default_img.jpg', upload_to='img/'),
        ),
    ]
