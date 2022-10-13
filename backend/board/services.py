from django.core.exceptions import ObjectDoesNotExist

from .models import Board, BoardData, BoardDataBasket
from users.models import User


def get_board(board_id):
    """Получение доски по id"""
    author = User.objects.get(pk=1)
    board = Board.objects.get_or_create(pk=board_id, defaults={'author': author})
    return board


def board_to_json(board_id):
    """Получение списка всех объектов доски по id доски в формате json"""
    get_board(board_id)
    board_data = BoardData.objects.filter(board=board_id).order_by('id')
    redo_objects = BoardDataBasket.objects.filter(board=board_id).order_by('id')
    return {"objects": [board_obj_to_json(obj) for obj in board_data],
            "redo_objects": [board_obj_to_json(obj) for obj in redo_objects]}


def board_obj_to_json(board_obj):
    """Получение данных в формате json"""
    type_object = str(board_obj.type_object)
    user = str(board_obj.user_update.username)
    return {"type": type_object, **board_obj.data, "id": str(board_obj.pk), "user": user}


def add_board_obj(board_id, object_data, user_id):
    """Добавление объекта доски в БД"""
    object_data = {**object_data}
    obj = BoardData(
        board_id=board_id,
        type_object=object_data.pop("type"),
        data=object_data,
        user_update=user_id,
    )
    obj.save()
    return obj


def undo(board_obj):
    """Обработка отмены действия на доске. Удаление объекта из BoardData  добавление этого объекта
     в BoardDataBasket"""
    try:
        object = BoardData.objects.get(id=int(board_obj['data']['id']))
        temp_object = BoardDataBasket(
            board_id=object.board_id,
            type_object=object.type_object,
            data=object.data,
            user_update=object.user_update,
        )
        temp_object.save()
        object.delete()
    except (TypeError, ObjectDoesNotExist, KeyError):
        pass


def redo(board_obj):
    """Обработка возврата действия на доске. Удаление объекта из BoardDataBasket  добавление этого объекта в
    BoardData """
    try:
        temp_object = BoardDataBasket.objects.get(id=int(board_obj['data']['id']))
        object = BoardData(
            board_id=temp_object.board_id,
            type_object=temp_object.type_object,
            data=temp_object.data,
            user_update=temp_object.user_update,
        )
        object.save()
        temp_object.delete()
    except (TypeError, ObjectDoesNotExist, KeyError):
        pass
