from django.core.management import call_command
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient
from users.models import User


class TestCabinetApp(APITestCase):
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

    def test_authorized_data(self):
        """Тест получения данных из кабинета авторизованного пользователя"""
        user = self.user_verify_data()
        user_db = self.login(user)
        url_profile = reverse('cabinet:profile',
                              kwargs={'username': user_db.username})
        response = self.client.get(url_profile)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('username'), user_db.username)
        self.assertEqual(response.data.get('email'), user_db.email)
        self.assertEqual(response.data.get('password'), user_db.password)
        self.assertEqual(response.data.get('first_name'), user_db.first_name)
        self.assertEqual(response.data.get('last_name'), user_db.last_name)
        url_profile = reverse('cabinet:profile',
                              kwargs={'username': 'user189'})
        response = self.client.get(url_profile)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_data(self):
        """Тест получения данных из кабинета неавторизованного пользователя"""
        user = self.user_verify_data()
        url_profile = reverse('cabinet:profile',
                              kwargs={'username': user['username']})
        response = self.client.get(url_profile)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_data(self):
        """Тест изменения данных пользователем в кабинете"""
        user = self.user_verify_data()
        user_db = self.login(user)
        user_new = self.new_user_data()
        url_profile = reverse('cabinet:profile',
                              kwargs={'username': user_db.username})
        response_get = self.client.get(url_profile)
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        response = self.client.patch(url_profile, data=user_new, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response_get.data.get('username'),
                            response.data.get('username'))
        self.assertNotEqual(response_get.data.get('first_name'),
                            response.data.get('first_name'))
        self.assertNotEqual(response_get.data.get('last_name'),
                            response.data.get('last_name'))
        self.assertEqual(response_get.data.get('email'),
                         response.data.get('email'))
        self.assertNotEqual(response_get.data.get('password'),
                            response.data.get('password'))
        new_user = self.get_user(user_db.email)
        url_profile = reverse('cabinet:profile',
                              kwargs={'username': new_user.username})
        response = self.client.get(url_profile)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_email(self):
        """Тест изменения почты пользователем в кабинете"""
        new_email = self.new_user_data()['email']
        user = self.user_verify_data()
        user_db = self.login(user)
        url_profile = reverse('cabinet:profile',
                              kwargs={'username': user_db.username})
        response = self.client.get(url_profile)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('email'), user['email'])
        url = reverse('cabinet:profile', kwargs={'username': user_db.username})
        response = self.client.patch(url, data={'email': new_email},
                                     format='json')
        email_old = response.data.get('email')
        activation_key = self.get_user(user_db.email).activation_key
        data_kwargs = {'email': user_db.email, 'new_email': new_email,
                       'activation_key': f'{activation_key}e'}
        url = reverse('cabinet:mail_update', kwargs=data_kwargs)
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(email_old, user_db.email)
        data_kwargs['activation_key'] = activation_key
        url = reverse('cabinet:mail_update', kwargs=data_kwargs)
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(email_old, response.data.get('email'))

    @staticmethod
    def user_verify_data():
        """Существующий верифицированный пользователь в базе"""
        return {
            'username': 'user1',
            'email': 'user1@example.com',
            'password': 'Qwerty123!',
        }

    @staticmethod
    def new_user_data():
        """Измененные данные в кабинете пользователя"""
        return {
            'first_name': 'Ivan',
            'last_name': 'Petrov',
            'email': 'test@local.local',
            'username': 'IvP',
            'password': 'Qwerty123!'
        }

    @staticmethod
    def get_user(email):
        """Получение пользователя из базы"""
        return User.objects.filter(email=email).first()
