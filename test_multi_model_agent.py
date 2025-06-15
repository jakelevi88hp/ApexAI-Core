import unittest
from unittest.mock import patch, Mock

from multi_model_agent import MultiModelAgent


class TestMultiModelAgent(unittest.TestCase):
    def setUp(self):
        self.agent = MultiModelAgent(models={"code": "code-model", "general": "general-model"}, verbose=False)

    def test_choose_model_code(self):
        result = self.agent.choose_model("build a csv parser")
        self.assertEqual(result, "code-model")

    def test_choose_model_default(self):
        result = self.agent.choose_model("tell a story")
        self.assertEqual(result, "general-model")

    @patch('multi_model_agent.subprocess.run')
    def test_self_update(self, mock_run):
        mock_run.return_value = Mock()
        self.agent.self_update()
        mock_run.assert_called_with([
            'git', 'pull'
        ], check=True, capture_output=True, text=True)


if __name__ == '__main__':
    unittest.main()
