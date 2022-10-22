# Generated by Django 4.1.1 on 2022-10-22 12:47

from django.db import migrations
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_user_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=users.models.LowercaseEmailField(max_length=254, unique=True),
        ),
    ]