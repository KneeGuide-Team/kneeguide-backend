from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .models import EmailOTP, User


@override_settings(ALLOWED_HOSTS=['testserver'])
class AuthLifecycleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.registration_payload = {
            'first_name': 'Test',
            'last_name': 'Patient',
            'email': '  New.Patient@Example.COM  ',
            'phone': '0550000000',
            'dob': '2001-09-02',
            'password': 'Contract1!',
            'role': 'patient',
        }

    def test_check_email_validates_and_matches_case_insensitively(self):
        User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='Contract1!',
            phone='0550000001',
        )

        cases = (
            ({'email': 'unused@example.com'}, 200, False),
            ({'email': 'EXISTING@EXAMPLE.COM'}, 200, True),
            ({'email': ''}, 400, None),
            ({'email': 'not-an-email'}, 400, None),
        )
        for payload, expected_status, expected_exists in cases:
            with self.subTest(payload=payload):
                response = self.client.post(
                    '/api/users/check-email/', payload, format='json'
                )
                self.assertEqual(response.status_code, expected_status)
                if expected_exists is not None:
                    self.assertEqual(response.data, {'exists': expected_exists})

    @patch('apps.users.views.send_otp_email')
    def test_registration_resend_verification_and_login_lifecycle(self, send_email):
        register_response = self.client.post(
            '/api/users/register/', self.registration_payload, format='json'
        )
        self.assertEqual(register_response.status_code, 201)
        self.assertEqual(register_response.data, {'message': 'OTP sent to email'})

        user = User.objects.get(email='new.patient@example.com')
        self.assertFalse(user.is_active)
        self.assertEqual(user.username, 'new.patient@example.com')
        send_email.assert_called_once()

        resend_response = self.client.post(
            '/api/users/resend-otp/',
            {'email': 'NEW.PATIENT@EXAMPLE.COM'},
            format='json',
        )
        self.assertEqual(resend_response.status_code, 200)
        self.assertEqual(resend_response.data, {'message': 'OTP resent'})
        self.assertEqual(EmailOTP.objects.filter(user=user).count(), 2)

        latest_otp = EmailOTP.objects.filter(user=user).last()
        verify_response = self.client.post(
            '/api/users/verify-otp/',
            {'email': 'NEW.PATIENT@EXAMPLE.COM', 'code': latest_otp.code},
            format='json',
        )
        self.assertEqual(verify_response.status_code, 200)
        self.assertEqual(verify_response.data, {'message': 'OTP verified'})

        login_response = self.client.post(
            '/api/users/login/',
            {
                'email': 'NEW.PATIENT@EXAMPLE.COM',
                'password': self.registration_payload['password'],
            },
            format='json',
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn('access', login_response.data)
        self.assertEqual(login_response.data['user']['role'], 'patient')

    @patch('apps.users.views.send_otp_email')
    def test_registration_rejects_case_variant_of_existing_email(self, send_email):
        User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='Contract1!',
            phone='0550000001',
        )
        payload = {**self.registration_payload, 'email': 'EXISTING@EXAMPLE.COM'}

        response = self.client.post('/api/users/register/', payload, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)
        send_email.assert_not_called()

    @patch('apps.users.views.send_otp_email', side_effect=RuntimeError('mail unavailable'))
    def test_failed_email_delivery_rolls_back_registration(self, _send_email):
        with self.assertRaises(RuntimeError):
            self.client.post(
                '/api/users/register/', self.registration_payload, format='json'
            )

        self.assertFalse(
            User.objects.filter(email='new.patient@example.com').exists()
        )
        self.assertEqual(EmailOTP.objects.count(), 0)
