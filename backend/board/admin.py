from django.contrib import admin

from board.models import Board, BoardData


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


admin.site.register(Board, BoardAdmin)
