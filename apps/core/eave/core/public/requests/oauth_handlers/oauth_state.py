from secrets import SystemRandom

UNICODE_ASCII_CHARACTER_SET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# copied from google
# https://github.com/oauthlib/oauthlib/blob/7d7fe904af504c20f7d802650e54a78e3d0be8ba/oauthlib/common.py#L188
def generate_token(length: int = 30, chars: str = UNICODE_ASCII_CHARACTER_SET) -> str:
    """Generates a non-guessable OAuth token
    OAuth (1 and 2) does not specify the format of tokens except that they
    should be strings of random characters. Tokens should not be guessable
    and entropy when generating the random characters is important. Which is
    why SystemRandom is used instead of the default random.choice method.
    """
    rand = SystemRandom()
    return "".join(rand.choice(chars) for x in range(length))
