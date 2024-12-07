import enum
from eave.stdlib.matched_str_enum import MatchedStrEnum

from .base import StdlibBaseTestCase


class MatchedStrEnumTest(StdlibBaseTestCase):
    async def test_matched_str_enum(self):
        # Adding a control to make sure that they behave differently.
        class _ControlEnum(enum.StrEnum):
            MEMBER_A = enum.auto()
            member_b = enum.auto()
            MemberC = enum.auto()

        assert _ControlEnum.MEMBER_A.value == "member_a"
        assert _ControlEnum.member_b.value == "member_b"
        assert _ControlEnum.MemberC.value == "memberc"

        class _TestEnum(MatchedStrEnum):
            MEMBER_A = enum.auto()
            member_b = enum.auto()
            MemberC = enum.auto()

        assert _TestEnum.MEMBER_A.value == "MEMBER_A"
        assert _TestEnum.member_b.value == "member_b"
        assert _TestEnum.MemberC.value == "MemberC"

        assert "MEMBER_A" in _TestEnum
        assert "member_b" in _TestEnum
        assert "MemberC" in _TestEnum
