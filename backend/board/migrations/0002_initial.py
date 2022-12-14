# Generated by Django 4.1.1 on 2022-09-06 15:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('board', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='boarddatabasket',
            name='user_update',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='добавил пользователь'),
        ),
        migrations.AddField(
            model_name='boarddata',
            name='board',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='board.board', verbose_name='доска'),
        ),
        migrations.AddField(
            model_name='boarddata',
            name='user_update',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='добавил пользователь'),
        ),
        migrations.AddField(
            model_name='board',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='автор'),
        ),
        migrations.AddField(
            model_name='board',
            name='group',
            field=models.ManyToManyField(blank=True, null=True, related_name='group', to=settings.AUTH_USER_MODEL, verbose_name='группа пользователей'),
        ),
    ]
