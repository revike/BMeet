from rest_framework import serializers

from board.models import BoardData


class BoardDataSerializer(serializers.ModelSerializer):
    """Сериализатор данных доски"""

    class Meta:
        model = BoardData
        fields = '__all__'
