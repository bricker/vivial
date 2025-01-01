import os
from typing import Any, override
from unittest import IsolatedAsyncioTestCase, TestCase
import unittest.mock

from eave.stdlib.test_helpers.base_mixin import BaseMixin


class MockingMixin(BaseMixin):
    active_mocks: dict[str, unittest.mock.Mock]
    _active_patches: dict[str, unittest.mock._patch]  # pyright: ignore [reportPrivateUsage, reportMissingTypeArgument]
    _active_patched_dicts: dict[str, unittest.mock._patch_dict]  # pyright: ignore [reportPrivateUsage]

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.active_mocks = {}
        self._active_patches = {}
        self._active_patched_dicts = {}

    @override
    async def cleanup(self) -> None:
        await super().cleanup()
        self.stop_all_patches()
        self.active_mocks.clear()
        self._active_patches.clear()
        self._active_patched_dicts.clear()

    @staticmethod
    async def mock_coroutine[T](value: T) -> T:
        return value

    def patch(
        self,
        patch: unittest.mock._patch,  # pyright: ignore [reportPrivateUsage, reportMissingTypeArgument]
        name: str | None = None,
        return_value: Any | None = None,
        side_effect: Any | None = None,
    ) -> unittest.mock.Mock:
        m = patch.start()
        m._testMethodName = self._testMethodName  # noqa: SLF001

        if name is None:
            if hasattr(patch.target, "__name__"):
                name = f"{patch.target.__name__}.{patch.attribute}"
            else:
                name = f"{patch.target}.{patch.attribute}"

        if return_value is not None:
            m.return_value = return_value

        if side_effect is not None:
            m.side_effect = side_effect

        self._active_patches[name] = patch
        self.active_mocks[name] = m
        return m

    def patch_env(self, values: dict[str, str | None], *, clear: bool = False) -> unittest.mock.Mock:
        # This method is the way it is so that we can pass in `None` to implicitly delete keys from os.environ.
        # Otherwise, os.environ only accepts string values, and setting an environment variable to an empty string is not the same as removing an environment variable.
        # i.e., an empty value is treated differently than a missing key in many cases.
        if clear:
            newenv: dict[str, str] = {}
        else:
            newenv = os.environ.copy()

        for k, v in values.items():
            if v is None:
                newenv.pop(k, None)
            else:
                newenv[k] = v

        m = self.patch_dict(name="env", patch=unittest.mock.patch.dict("os.environ", newenv, clear=True))
        return m

    def patch_dict(self, patch: unittest.mock._patch_dict, name: str | None = None) -> unittest.mock.Mock:  # pyright: ignore [reportPrivateUsage]
        name = name or str(patch.in_dict)
        mock = patch.start()
        self._active_patched_dicts[name] = patch
        self.active_mocks[name] = mock
        return mock

    def get_mock(self, name: str) -> unittest.mock.Mock:
        assert name in self.active_mocks, f"{name} is not patched!"
        return self.active_mocks[name]

    def get_patch(self, name: str) -> unittest.mock._patch:  # pyright: ignore [reportPrivateUsage, reportMissingTypeArgument]
        assert name in self._active_patches, f"{name} is not patched!"
        return self._active_patches[name]

    def get_patched_dict(self, name: str) -> unittest.mock._patch_dict:  # pyright: ignore [reportPrivateUsage]
        assert name in self._active_patched_dicts, f"{name} is not patched!"
        return self._active_patched_dicts[name]

    def stop_patch(self, name: str) -> None:
        assert name in self._active_patches, f"{name} is not patched!"
        self.get_patch(name).stop()

    def stop_all_patches(self) -> None:
        unittest.mock.patch.stopall()
