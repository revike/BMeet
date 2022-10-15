from django.core.exceptions import ObjectDoesNotExist
from quopri import decodestring
from .models import Board, BoardData, BoardDataBasket


def decode_query_string_value(value):
    """Декодирование строки запроса"""
    value_bytes = bytes(value.replace('%', '=').replace("+", " "), 'UTF-8')
    value_decode_str = decodestring(value_bytes)
    return value_decode_str.decode('UTF-8')


def has_access(board_id, user, board_name):
    """Проверка имеет ли право пользователь user подключится к доске board_id"""
    try:
        board = Board.objects.get(pk=board_id, is_active=True)
        board_name = decode_query_string_value(board_name)
        if (user in board.group.all()) and (board_name == board.name):
            return True
    except ObjectDoesNotExist:
        return False
    return False


def board_to_json(board_id, user_id):
    """Получение списка всех объектов доски по id доски в формате json"""
    board_data = BoardData.objects.filter(board=board_id).order_by('id')
    redo_object = BoardDataBasket.objects.filter(board=board_id, user_update=user_id).order_by('-id').first()
    undo_object = BoardData.objects.filter(board=board_id, user_update=user_id).order_by('-id').first()
    return {"objects": [board_obj_to_json(obj) for obj in board_data],
            "redo_object": board_obj_to_json(redo_object),
            "undo_object": board_obj_to_json(undo_object),
            }


def board_obj_to_json(board_obj):
    """Получение данных в формате json"""
    if board_obj is None:
        return {}
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
