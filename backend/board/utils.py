from board.models import Board, NoRegisterUser
from board.serializers import GroupSerializer
from users.models import User
from board.tasks import send_mail_add_group


class AddUserBoardMixin:
    """Mixin для оповещения пользователя о приглашение в группу"""

    @staticmethod
    def save_serializer(request, serializer, group_data):
        """Сохранение данных в базе"""
        author = request.user
        email_list_no_register = set()
        email_list_register = set()
        group = {author}
        if group_data:
            GroupSerializer(data=group_data, many=True).is_valid(
                raise_exception=True)
            for email in group_data:
                user = User.objects.filter(
                    email=email['email']).select_related().first()
                if user:
                    if author.email == email['email']:
                        continue
                    group.add(user.id)
                    email_list_register.add(email['email'])
                else:
                    email_list_no_register.add(email['email'])

        serializer.save(author=author, group=group)
        return email_list_register, email_list_no_register

    @staticmethod
    def sending_newsletter(serializer, email_list_register,
                           email_list_no_register, email_black_list=None):
        """Отправка писем"""
        if email_black_list is None:
            email_black_list = set()
        board_id = serializer.data.get('id')
        if email_list_register:
            result_email_register = list(
                email_list_register - email_black_list)
            for email in result_email_register:
                send_mail_add_group.delay(email, board_id)
        if email_list_no_register:
            result_email_no_register = list(
                email_list_no_register - email_black_list)
            board = Board.objects.get(id=board_id)
            for email in result_email_no_register:
                send_mail_add_group.delay(email, board_id)
                NoRegisterUser.objects.create(board=board, email=email)

