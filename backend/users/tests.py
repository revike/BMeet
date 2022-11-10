from django.contrib.auth.hashers import make_password
from django.core.management import call_command
from django.urls import resolve
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from users.models import User
from users.views import RegisterApiView, LoginApiView, ResendApiView, \
    VerificationKeyApiView, LogoutApiView, RecoveryPasswordApiView, \
    GeneratePasswordApiView


class TestUsersApp(APITestCase):
    """Тестирование приложения users"""

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

    def test_register_user(self):
        """Тест регистрации нового пользователя с верными данными"""
        url = reverse('users:register')
        user = self.new_user_data()
        response = self.client.post(url, data=user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user = self.get_user(user['email'])
        self.assertTrue(new_user)
        self.assertFalse(new_user.is_verify)
        self.assertEquals(resolve(url).func.view_class, RegisterApiView)

    def test_register_user_error(self):
        """Тест регистрации нового пользователя с неверными данными"""
        url = reverse('users:register')
        user = self.new_user_data_error()
        response = self.client.post(url, data=user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.get_user(user['email']))
        self.assertEquals(resolve(url).func.view_class, RegisterApiView)

    def test_register_old_user(self):
        """Тест регистрации существующего пользователя"""
        url = reverse('users:register')
        user = self.user_data()
        response = self.client.post(url, data=user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(user)
        self.assertEquals(resolve(url).func.view_class, RegisterApiView)

    def test_login_user(self):
        """Тест входа на сайт верифицированного пользователя"""
        user = self.user_data()
        self.login(user)

    def test_login_user_no_verify(self):
        """Тест входа на сайт не верифицированного пользователя"""
        url = reverse('users:login')
        user = self.user_data_no_verify()
        del user['username']
        response = self.client.post(url, data=user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        user_db = self.get_user(user['email'])
        self.assertFalse(user_db.is_verify)
        self.assertEquals(resolve(url).func.view_class, LoginApiView)
        token_db = Token.objects.filter(user=user_db).first()
        token_response = response.data.get('token')
        self.assertFalse(token_db)
        self.assertFalse(token_response)

    def test_login_user_no_active(self):
        """Тест входа на сайт не активного пользователя"""
        url = reverse('users:login')
        user = self.user_data_no_active()
        del user['username']
        response = self.client.post(url, data=user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        user_db = self.get_user(user['email'])
        self.assertFalse(user_db.is_active)
        self.assertEquals(resolve(url).func.view_class, LoginApiView)
        token_db = Token.objects.filter(user=user_db).first()
        token_response = response.data.get('token')
        self.assertFalse(token_db)
        self.assertFalse(token_response)

    def test_resend_email(self):
        """Тест повторной отправки письма"""
        user_new = self.new_user_data()
        url = reverse('users:register')
        response = self.client.post(url, data=user_new)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = self.get_user(user_new['email'])
        self.assertFalse(user.is_verify)
        user.password = make_password(user.password)
        user.save()
        url = reverse('users:resend_email', kwargs={'pk': user.pk})
        response = self.client.patch(url, data=user_new)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url_error = reverse('users:resend_email', kwargs={'pk': user.pk - 1})
        response = self.client.patch(url_error, data=user_new)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        del user_new['email']
        url = reverse('users:resend_email', kwargs={'pk': user.pk})
        response = self.client.patch(url, data=user_new)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(resolve(url).func.view_class, ResendApiView)

    def test_verify_user(self):
        """Тест верификации пользователя"""
        user_no_verify = self.user_data_no_verify()
        user = self.get_user(user_no_verify['email'])
        url_error = reverse(
            'users:verify',
            kwargs={
                'email': user.email,
                'activation_key': f'{user.activation_key}e'
            }
        )
        url = reverse(
            'users:verify',
            kwargs={'email': user.email, 'activation_key': user.activation_key}
        )
        response = self.client.patch(url_error)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user = self.get_user(user_no_verify['email'])
        self.assertFalse(user.is_verify)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = self.get_user(user_no_verify['email'])
        self.assertTrue(user.is_verify)
        self.assertEquals(resolve(url).func.view_class, VerificationKeyApiView)

    def test_logout(self):
        """Тест logout"""
        user = self.user_data()
        self.login(user)
        url_logout = reverse('users:logout')
        response = self.client.get(url_logout)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(url_logout)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEquals(resolve(url_logout).func.view_class, LogoutApiView)

    def test_recovery_password(self):
        """Тест восстановления пароля"""
        user_error = self.new_user_data_error()
        user = self.get_user(user_error['email'])
        self.assertFalse(user)
        url = reverse('users:send_recovery',
                      kwargs={'email': user_error['email']})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user = self.user_data()
        user_db = self.get_user(user['email'])
        self.assertTrue(user_db)
        url = reverse('users:send_recovery',
                      kwargs={'email': user['email']})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(resolve(url).func.view_class,
                          RecoveryPasswordApiView)

    def test_generate_new_password(self):
        """Тест генерации нового пароля"""
        user = self.user_data()
        user_db = self.get_user(user['email'])
        password_old = user_db.password
        self.assertTrue(user_db)
        url_send = reverse('users:send_recovery',
                           kwargs={'email': user['email']})
        response = self.client.patch(url_send)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_db = self.get_user(user['email'])
        url = reverse('users:recovery',
                      kwargs={'email': user_db.email,
                              'activation_key': f'{user_db.activation_key}'})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_db = self.get_user(user['email'])
        password_new = user_db.password
        self.assertEquals(resolve(url).func.view_class,
                          GeneratePasswordApiView)
        self.assertNotEqual(password_new, password_old)

    @staticmethod
    def new_user_data():
        """Верные данные нового пользователя"""
        return {
            'username': 'user_new',
            'email': 'user_new@example.com',
            'password': 'Qwerty123!',
        }

    @staticmethod
    def new_user_data_error():
        """Неверные данные пользователя"""
        return {
            'username': 'user10',
            'email': 'user10',
            'password': 'Qwerty123!',
        }

    @staticmethod
    def user_data():
        """Существующий верифицированный пользователь в базе"""
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
    def user_data_no_active():
        """Существующий не активный пользователь в базе"""
        return {
            'username': 'user6',
            'email': 'user6@example.com',
            'password': 'Qwerty123!',
        }

    @staticmethod
    def get_user(email):
        """Получение пользователя из базы"""
        return User.objects.filter(email=email).first()
