from django.db import models
from users.models import User, LowercaseEmailField


class Board(models.Model):
    """Доска"""

    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )
    group = models.ManyToManyField(
        User,
        blank=True,
        related_name='group',
        verbose_name='группа пользователей',
    )
    name = models.CharField(
        max_length=128,
        verbose_name='название',
    )
    description = models.TextField(
        blank=True,
        verbose_name='описание',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='активна',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='создано',
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name='обновлено',
    )

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = 'board'
        verbose_name = 'Доска'
        verbose_name_plural = 'Доски'
        ordering = ['id']


class BoardData(models.Model):
    """Объекты на доске"""

    TYPE_CHOICES = (
        ('v', 'векторная графика'),
        ('r', 'растровая графика')
    )

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        verbose_name='доска',
    )
    type_object = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES,
        verbose_name='тип объекта',
    )
    data = models.JSONField(
        verbose_name='объект доски',
    )
    user_update = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='добавил пользователь',
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name='обновлено',
    )
    created = models.DateTimeField(
        auto_now=True,
        verbose_name='обновлено',
    )

    def __str__(self):
        return f'{self.board.name}'

    class Meta:
        db_table = 'board_data'
        verbose_name = 'Объект на доске'
        verbose_name_plural = 'Объекты на доске'


class BoardDataBasket(models.Model):
    """Последние удаленные с доски объекты"""

    TYPE_CHOICES = (
        ('v', 'векторная графика'),
        ('r', 'растровая графика')
    )

    TYPE_CHOICES_ACTION = (
        ('u', 'undo'),
        ('r', 'redo')
    )

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        verbose_name='доска',
    )
    type_object = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES,
        verbose_name='тип объекта',
    )
    type_object_action = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES_ACTION,
        verbose_name='тип действия над объектом',
    )
    temp_id = models.IntegerField(
        blank=True,
        null=True,
        default=False,
        verbose_name='id объекта в доске',
    )
    data = models.JSONField(
        verbose_name='объект доски',
    )
    user_update = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='добавил пользователь',
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name='обновлено',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='создано',
    )

    def __str__(self):
        return f'{self.board.name}'

    class Meta:
        db_table = 'board_data_basket'
        verbose_name = 'Удаленный объект'
        verbose_name_plural = 'Удаленные объекты'


class NoRegisterUser(models.Model):
    """Незарегистрированные приглашенные пользователи"""
    board = models.ForeignKey('Board', on_delete=models.CASCADE, null=True,
                              verbose_name='доска')
    email = LowercaseEmailField(unique=False, verbose_name='email')

    def __str__(self):
        return f'{self.email}'