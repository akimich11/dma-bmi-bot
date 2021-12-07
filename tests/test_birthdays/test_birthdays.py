import unittest

from unittest.mock import patch, MagicMock

from birthdays.periodic import check_birthdays


class BirthdayCheckTestCase(unittest.TestCase):
    @patch('birthdays.periodic.send_greetings')
    @patch('birthdays.periodic.datetime.datetime')
    @patch('birthdays.periodic.user_model')
    def test_periodic_check(self, user_model_patch, datetime_patch, send_greetings_patch):
        now_mock = MagicMock()
        now_date = MagicMock()
        user_mock = MagicMock()
        user_mock.first_name = MagicMock()
        user_mock.birthday = now_date
        user_model_patch.users = {1: MagicMock(), 2: user_mock, 3: MagicMock()}
        user_model_patch.update_next_birthday = MagicMock()
        datetime_patch.now.return_value = now_mock
        now_mock.date.return_value = now_date

        result = check_birthdays()

        self.assertIsNone(result)
        self.assertEqual(3, now_mock.date.call_count)
        send_greetings_patch.assert_called_once_with(user_mock.first_name)
        user_model_patch.update_next_birthday.assert_called_once_with(user_mock)


if __name__ == '__main__':
    unittest.main()
