from django.contrib import admin

from board.models import Board, BoardData, BoardMessage


class InlineBoardData(admin.StackedInline):
    model = BoardData
    extra = 0


class BoardAdmin(admin.ModelAdmin):
    inlines = [InlineBoardData]
    list_display = ('id', 'author', 'name',)
    list_display_links = ('id', 'author', 'name',)
    fields = (
        'id', 'author', 'group', 'name', 'description', 'is_active', 'created',
        'updated',)
    readonly_fields = ('id', 'created', 'updated',)


class BoardMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'datetime',)
    list_display_links = ('id', 'user_id', 'datetime',)
    list_filter = ('datetime',)


admin.site.register(Board, BoardAdmin)
admin.site.register(BoardMessage, BoardMessageAdmin)
