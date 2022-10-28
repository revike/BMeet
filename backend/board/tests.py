from django.core.management import call_command
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from users.models import User
from board.models import Board


class TestBoardApp(APITestCase):
    def setUp(self) -> None:
        call_command('flush', '--noinput')
        call_command('loaddata', 'test_db.json')
        self.client = APIClient()

    def login(self, user):
        url_login = reverse('users:login')
        del user['username']
        response = self.client.post(url_login, data=user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_db = self.get_user(user['email'])
        token_db = Token.objects.filter(user=user_db).first().key
        token_response = response.data.get('token').split()[1]
        self.assertEqual(token_db, token_response)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token_response}')
        return user_db

    def test_unauthorized_boards(self):
        """Тест получения доступа к доскам неавторизованного пользователя"""
        url_boards = reverse('board:boards')
        response = self.client.get(url_boards)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_boards(self):
        """Тест получения доступа к доскам авторизованного пользователя"""
        user = self.user_verify_data()
        self.login(user)
        url_boards = reverse('board:boards')
        response = self.client.get(url_boards)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authorized_board(self):
        """Тест получения доступа к доске авторизованного пользователя"""
        user = self.user_verify_data()
        self.login(user)
        board = self.created_board()
        board_db = self.get_board(board['pk'])
        url_board = reverse('board:board_detail', kwargs={'pk': board_db.pk})
        response = self.client.get(url_board)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('name'), board_db.name)
        self.assertEqual(response.data.get('description'), board_db.description)
        groups = response.data.get('group')
        self.assertEqual(groups[0]['email'], board_db.group.first().email)
        url_board = reverse('board:board_detail', kwargs={'pk': 12345})
        response = self.client.get(url_board)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_board(self):
        """Тест получения доступа к доске неавторизованного пользователя"""
        board = self.created_board()
        board_db = self.get_board(board['pk'])
        url_board = reverse('board:board_detail', kwargs={'pk': board_db.pk})
        response = self.client.get(url_board)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_board(self):
        """Тест изменения данных доски пользователем"""
        user = self.user_verify_data()
        self.login(user)
        board = self.created_board()
        board_db = self.get_board(board['pk'])
        board_new = self.update_board()
        url_board = reverse('board:board_detail', kwargs={'pk': board_db.pk})
        response = self.client.get(url_board)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url_update = reverse('board:update', kwargs={'pk': board_db.pk})
        response_patch = self.client.put(url_update, data=board_new, format='json')
        self.assertEqual(response_patch.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response_patch.data.get('name'),
                            response.data.get('name'))
        self.assertNotEqual(response_patch.data.get('description'),
                            response.data.get('description'))

    def test_update_board_other_user(self):
        """Тест редактирования данных доски другим пользователем"""
        user_other = self.user_verify_data_other()
        self.login(user_other)
        board = self.created_board()
        board_db = self.get_board(board['pk'])
        board_new = self.update_board()
        url_update = reverse('board:update', kwargs={'pk': board_db.pk})
        response_patch = self.client.put(url_update, data=board_new, format='json')
        self.assertEqual(response_patch.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_board_other_user(self):
        """Тест просмотра чужой доски без приглашения"""
        user_other = self.user_verify_data_other()
        self.login(user_other)
        board = self.created_board()
        board_db = self.get_board(board['pk'])
        url_board = reverse('board:board_detail', kwargs={'pk': board_db.pk})
        response_patch = self.client.get(url_board)
        self.assertEqual(response_patch.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_board_other_user(self):
        """Тест удаления доски другим пользователем"""
        user_other = self.user_verify_data_other()
        self.login(user_other)
        board = self.created_board()
        board_db = self.get_board(board['pk'])
        url_update = reverse('board:delete', kwargs={'pk': board_db.pk})
        response = self.client.delete(url_update)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_board(self):
        """Тест удаления доски пользователем"""
        user = self.user_verify_data()
        self.login(user)
        board = self.created_board()
        board_db = self.get_board(board['pk'])
        url_board = reverse('board:board_detail', kwargs={'pk': board_db.pk})
        response = self.client.get(url_board)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url_delete = reverse('board:delete', kwargs={'pk': board_db.pk})
        response = self.client.delete(url_delete)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_data_delete_board(self):
        """Тест получения доступа к удаленной доске пользователем"""
        user = self.user_verify_data()
        self.login(user)
        board = self.deleted_board()
        board_db = self.get_board(board['pk'])
        url_board = reverse('board:board_detail', kwargs={'pk': board_db.pk})
        response = self.client.get(url_board)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @staticmethod
    def user_verify_data():
        """Существующий верифицированный пользователь в базе"""
        return {
            'username': 'user2',
            'email': 'user2@example.com',
            'password': 'Qwerty123!',
        }

    @staticmethod
    def user_verify_data_other():
        """Существующий верифицированный приглашенный пользователь в базе"""
        return {
            'username': 'user1',
            'email': 'user1@example.com',
            'password': 'Qwerty123!',
        }

    @staticmethod
    def user_data_no_verify():
        """Существующий не верифицированный пользователь в базе"""
        return {
            'username': 'user4',
            'email': 'user4@example.com',
            'password': 'Qwerty123!',
        }

    @staticmethod
    def user_verify_data_two():
        """Второй существующий верифицированный пользователь в базе"""
        return {
            'username': 'user1',
            'email': 'user1@example.com',
            'password': 'Qwerty123!',
        }

    @staticmethod
    def created_board():
        """Описание доски"""
        return {
            'pk': 2,
            'author': 3,
            'name': 'board',
            'description': 'desc',
            'group': [
                3
            ]
        }

    @staticmethod
    def deleted_board():
        """Описание удаленной доски"""
        return {
            'pk': 3,
            'author': 3,
            'name': 'board delete',
            'description': 'delete',
            "group": [
                3
            ]
        }

    @staticmethod
    def update_board():
        """Редактирование доски"""
        return {
            'name': 'my_board',
            'description': 'boards'
        }

    @staticmethod
    def get_user(email):
        """Получение пользователя из базы"""
        return User.objects.filter(email=email).first()

    @staticmethod
    def get_board(pk):
        """Получение доски из базы"""
        return Board.objects.filter(pk=pk).first()
