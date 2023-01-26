from django.core.exceptions import ObjectDoesNotExist

from .models import Board, BoardData, BoardDataBasket, BoardMessage


def has_access(board_id, user):
    """Проверка имеет ли право пользователь user
    подключится к доске board_id"""
    try:
        board = Board.objects.prefetch_related('group').get(pk=board_id,
                                                            is_active=True)
        if user in board.group.all():
            return True
    except ObjectDoesNotExist:
        return False
    return False


def board_to_json(board_id, user_id):
    """Получение списка всех объектов доски по id доски в формате json"""
    board_data = BoardData.objects.select_related('user_update').filter(
        board=board_id).order_by('id')
    objects = BoardDataBasket.objects.select_related('user_update').filter(
        board=board_id, user_update=user_id)
    redo_object = objects.filter(type_object_action='r').order_by('id').first()
    undo_object = objects.filter(type_object_action='u').order_by(
        '-id').first()
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
    return {"type": type_object, **board_obj.data, "id": str(board_obj.pk),
            "user": user}


def add_board_obj_basket(board_obj, type_object_action):
    """Добавление объекта доски в BardDataBasket"""
    obj = BoardDataBasket(
        board_id=board_obj.board_id,
        type_object=board_obj.type_object,
        data=board_obj.data,
        user_update=board_obj.user_update,
        temp_id=board_obj.pk,
        type_object_action=type_object_action
    )
    obj.save()
    return obj


def add_board_obj(board_id, object_data, user_id):
    """Добавление объекта доски в BardData"""
    object_data = {**object_data}
    type_object = object_data.pop("type")
    obj = BoardData(
        board_id=board_id,
        type_object=type_object,
        data=object_data,
        user_update=user_id,
    )
    obj.save()
    undo_obj = add_board_obj_basket(board_obj=obj, type_object_action='u')
    undo_obj = board_obj_to_json(undo_obj)
    obj = board_obj_to_json(obj)
    return obj, undo_obj


def undo(board_obj):
    """Обработка отмены действия на доске. Удаление объекта из BoardData
     добавление этого объекта в BoardDataBasket"""
    try:
        temp_object = BoardDataBasket.objects.get(
            id=int(board_obj['data']['id']))
        object_ = BoardData.objects.filter(id=temp_object.temp_id)
        object_.delete()
        temp_object.type_object_action = 'r'
        temp_object.temp_id = False
        temp_object.save()
    except (TypeError, ObjectDoesNotExist, KeyError, AttributeError):
        pass


def redo(board_obj):
    """Обработка возврата действия на доске. Удаление объекта из
    BoardDataBasket добавление этого объекта в BoardData """
    try:
        temp_object = BoardDataBasket.objects.get(
            id=int(board_obj['data']['id']))
        temp_object.data["type"] = temp_object.type_object
        add_board_obj(board_id=temp_object.board_id,
                      object_data=temp_object.data,
                      user_id=temp_object.user_update)
        temp_object.delete()
    except (TypeError, ObjectDoesNotExist, KeyError, AttributeError):
        pass


def delete_board_data_basket_objects(board_id, user):
    """Удаление объектов, созданных user из
    BoardDataBasket для доски board_id"""
    BoardDataBasket.objects.select_related('user_update').filter(
        user_update=user, board_id=board_id).delete()


def delete_redo_objects(board_id, user):
    """Удаление redo объектов, созданных user из
    BoardDataBasket для доски board_id"""
    BoardDataBasket.objects.select_related('user_update').filter(
        user_update=user, board_id=board_id,
        type_object_action='r').delete()


def clear_chat_from_database(board_id):
    """Удаление сообщений из чата"""
    BoardMessage.objects.filter(board_id=board_id).delete()
