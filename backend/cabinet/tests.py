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

    def test_authorized_data(self):
        """Тест получения данных из кабинета авторизованного пользователя"""
        url_login = reverse('users:login')
        user = self.user_verify_data()
        del user['username']
        response = self.client.post(url_login, data=user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_db = self.get_user(user['email'])
        token_db = Token.objects.filter(user=user_db).first().key
        token_response = response.data.get('token').split()[1]
        self.assertEqual(token_db, token_response)
        url_logout = reverse('users:logout')
        response = self.client.get(url_logout)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token_response}')
        user = self.user_verify_data()
        url_profile = reverse('cabinet:profile', kwargs={'username': user['username']})
        response = self.client.get(url_profile)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_data(self):
        """Тест получения данных из кабинета неавторизованного пользователя"""
        user = self.user_verify_data()
        url_profile = reverse('cabinet:profile', kwargs={'username': user['username']})
        response = self.client.get(url_profile)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_data(self):
        """Тест изменения данных пользователем в кабинете"""
        url_login = reverse('users:login')
        user_new = self.new_user_data()
        user = self.user_verify_data()
        del user['username']
        response = self.client.post(url_login, data=user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_db = self.get_user(user['email'])
        token_db = Token.objects.filter(user=user_db).first().key
        token_response = response.data.get('token').split()[1]
        self.assertEqual(token_db, token_response)
        url_logout = reverse('users:logout')
        response = self.client.get(url_logout)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token_response}')
        user = self.user_verify_data()
        url_profile = reverse('cabinet:profile', kwargs={'username': user['username']})
        response = self.client.put(url_profile, data=user_new)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_change_email(self):
        """Тест изменения почты пользователем в кабинете"""
        user_no_verify = self.user_data_no_verify()
        user = self.get_user(user_no_verify['email'])
        user_verify = self.user_verify_data()
        url_error = reverse(
            'cabinet:mail_update',
            kwargs={
                'email': user.email,
                'new_email': user.email,
                'activation_key': f'{user.activation_key}e'
            }
        )
        url = reverse(
            'cabinet:mail_update',
            kwargs={'email': user.email, 'new_email': user.email, 'activation_key': user.activation_key}
        )
        response = self.client.patch(url_error)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user = self.get_user(user_no_verify['email'])
        self.assertFalse(user.is_verify)

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = self.get_user(user_verify['email'])
        self.assertTrue(user.is_verify)
        self.assertEquals(resolve(url).func.view_class, UpdateEmailApiView)

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
