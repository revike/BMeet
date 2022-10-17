import json
from django.core.management import call_command
from django.urls import resolve
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient
from users.models import User
from cabinet.views import UpdateEmailApiView


class TestCabinetApp(APITestCase):
    def setUp(self) -> None:
        call_command('flush', '--noinput')
        call_command('loaddata', 'test_db.json')
        self.client = APIClient()

    def logIn(self):
        url_login = reverse('users:login')
        user = self.user_verify_data()
        del user['username']
        response = self.client.post(url_login, data=user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_db = self.get_user(user['email'])
        token_db = Token.objects.filter(user=user_db).first().key
        token_response = response.data.get('token').split()[1]
        self.assertEqual(token_db, token_response)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token_response}')
        return user_db

    def test_authorized_data(self):
        """Тест получения данных из кабинета авторизованного пользователя"""
        user_db = self.logIn()
        user = self.user_verify_data()
        url_profile = reverse('cabinet:profile', kwargs={'username': user['username']})
        response = self.client.get(url_profile)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('username'), user_db.username)
        self.assertEqual(response.data.get('email'), user_db.email)
        self.assertEqual(response.data.get('password'), user_db.password)
        self.assertEqual(response.data.get('first_name'), user_db.first_name)
        self.assertEqual(response.data.get('last_name'), user_db.last_name)
        url_profile = reverse('cabinet:profile', kwargs={'username': 'user189'})
        response = self.client.get(url_profile)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_data(self):
        """Тест получения данных из кабинета неавторизованного пользователя"""
        user = self.user_verify_data()
        url_profile = reverse('cabinet:profile', kwargs={'username': user['username']})
        response = self.client.get(url_profile)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_data(self):
        """Тест изменения данных пользователем в кабинете"""
        user_new = self.new_user_data()
        user_db = self.logIn()
        user = self.user_verify_data()
        password_old = user_db.password
        url_profile = reverse('cabinet:profile', kwargs={'username': user['username']})
        response = self.client.get(url_profile)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(url_profile, data=user_new)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_db = self.get_user(user['email'])
        password_new = user_db.password
        response = json.loads(response.content)
        self.assertEqual(response['username'], 'IvP')
        self.assertEqual(response['first_name'], 'Ivan')
        self.assertEqual(response['last_name'], 'Petrov')
        self.assertEqual(response['email'], 'user1@example.com')
        self.assertNotEqual(password_new, password_old)
        url_profile = reverse('cabinet:profile', kwargs={'username': user['username']})
        response = self.client.get(url_profile)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_email(self):
        """Тест изменения почты пользователем в кабинете"""
        user_verify = self.user_verify_data()
        users = self.get_user(user_verify['email'])
        self.logIn()
        user_verify = self.user_verify_data()
        url_profile = reverse('cabinet:profile', kwargs={'username': user_verify['username']})
        response = self.client.get(url_profile)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = json.loads(response.content)
        self.assertEqual(response['email'], 'user1@example.com')
        url_error = reverse(
            'cabinet:mail_update',
            kwargs={
                'email': users.email,
                'new_email': 'usernew@example.com',
                'activation_key': f'{users.activation_key}e'
            }
        )
        url = reverse(
            'cabinet:mail_update',
            kwargs={'email': users.email, 'new_email': 'usernew@example.com', 'activation_key': users.activation_key}
        )
        response = self.client.patch(url_error)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(resolve(url).func.view_class, UpdateEmailApiView)
        response = json.loads(response.content)
        self.assertEqual(response['email'], 'usernew@example.com')
        response = self.client.get(url_profile)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @staticmethod
    def user_verify_data():
        """Существующий верифицированный пользователь в базе"""
        return {
            'username': 'user1',
            'email': 'user1@example.com',
            'password': 'user',
        }

    @staticmethod
    def new_user_data():
        """Измененные данные в кабинете пользователя"""
        return {
            'first_name': 'Ivan',
            'last_name': 'Petrov',
            'username': 'IvP',
            'password': '555qwe'
        }

    @staticmethod
    def user_data_no_verify():
        """Существующий не верифицированный пользователь в базе"""
        return {
            'username': 'user4',
            'email': 'user4@example.com',
            'password': 'user',
        }

    @staticmethod
    def get_user(email):
        """Получение пользователя из базы"""
        return User.objects.filter(email=email).first()
