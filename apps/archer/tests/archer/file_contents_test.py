import tiktoken
from eave.archer.file_contents import get_file_contents, truncate_file_contents_for_model
from eave.stdlib.openai_client import OpenAIModel
from eave.stdlib.test_util import UtilityBaseTestCase

class FileContentsTests(UtilityBaseTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.t = {}
        self._data_model = OpenAIModel.GPT_35_TURBO_16K
        self._data_contents_long = self.load_relative_file("lorem/long.txt", __file__)
        self._data_contents_short = self.load_relative_file("lorem/short.txt", __file__)
        self._encoding = tiktoken.encoding_for_model(self._data_model)

    async def test_get_file_contents(self):
        contents = get_file_contents(self.relative_file_path("lorem/short.txt", __file__))
        assert contents == self._data_contents_short

    async def test_file_contents_truncated(self):
        contents = truncate_file_contents_for_model(self._data_contents_long, self._data_model, step=200)

        actual_tokens = self._encoding.encode(self._data_contents_long)
        returned_tokens = self._encoding.encode(contents)
        assert len(returned_tokens) <= len(actual_tokens)
        assert len(returned_tokens) <= self._data_model.max_tokens

    async def test_file_contents_not_truncated(self):
        contents = truncate_file_contents_for_model(self._data_contents_short, self._data_model, step=200)


        actual_tokens = self._encoding.encode(self._data_contents_short)
        returned_tokens = self._encoding.encode(contents)
        assert len(returned_tokens) == len(actual_tokens)
        assert len(returned_tokens) <= self._data_model.max_tokens
