from .models import Board, BoardData
from users.models import User


def get_board(board_id):
    """Получение доски по id"""
    author = User.objects.get(pk=1)
    board = Board.objects.get_or_create(pk=board_id,
                                        defaults={'author': author})
    return board


def board_to_json(board_id):
    """Получение списка всех объектов доски по id доски в формате json"""
    get_board(board_id)
    board_data = BoardData.objects.filter(board=board_id)
    return {"objects": [board_obj_to_json(obj) for obj in board_data]}


def board_obj_to_json(board_obj):
    """Получение данных в формате json"""
    type_object = str(board_obj.type_object)
    return {"type": type_object, **board_obj.data, "id": str(board_obj.pk)}


def add_board_obj(board_id, object_data):
    """Добавление объекта доски в БД"""
    object_data = {**object_data}
    obj = BoardData(
        board_id=board_id,
        type_object=object_data.pop("type"),
        data=object_data,
    )
    obj.save()
    return obj
