import enum

EAVE_ERROR_CODE_QP = "ev_error_code"


class EaveOnboardingErrorCode(enum.StrEnum):
    already_linked = "already_linked"


class EaveSignUpErrorCode(enum.StrEnum):
    invalid_email = "invalid_email"  # depended on in dashboard AuthenticationPage/index.tsx:AuthErrorCodes enum
