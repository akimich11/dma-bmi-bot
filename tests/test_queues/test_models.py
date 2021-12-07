import unittest
from unittest.mock import MagicMock, patch
from queues.models import QueueModel, Queue


class ModelsTestCase(unittest.TestCase):
    @patch('queues.models.user_model')
    def test_cancel_sign_up_shift_true(self, user_model_patch):
        QueueModel._read_database = MagicMock()
        queue_model = QueueModel()
        queue_name_mock = MagicMock()

        user_id = 200
        user_model_patch.users = {user_id: MagicMock()}

        queue_model._get_queue = MagicMock()
        queue_model._update_queue = MagicMock()
        queue_mock = Queue(queue_name_mock, {100: 1, 200: 3, 300: 5, 400: 8})
        queue_model._get_queue.return_value = queue_mock

        result = queue_model.cancel_sign_up(queue_name_mock, user_id, is_shift=True)

        self.assertEqual(result, queue_name_mock)
        self.assertEqual(queue_mock.positions, {100: 1, 300: 4, 400: 7})

    @patch('queues.models.user_model')
    def test_cancel_sign_up_shift_false(self, user_model_patch):
        QueueModel._read_database = MagicMock()
        queue_model = QueueModel()
        queue_name_mock = MagicMock()

        user_id = 200
        user_model_patch.users = {user_id: MagicMock()}

        queue_model._get_queue = MagicMock()
        queue_model._update_queue = MagicMock()
        queue_mock = Queue(queue_name_mock, {100: 1, 200: 3, 300: 5, 400: 8})
        queue_model._get_queue.return_value = queue_mock

        result = queue_model.cancel_sign_up(queue_name_mock, user_id, is_shift=False)

        self.assertEqual(result, queue_name_mock)
        self.assertEqual(queue_mock.positions, {100: 1, 300: 5, 400: 8})


if __name__ == '__main__':
    unittest.main()
