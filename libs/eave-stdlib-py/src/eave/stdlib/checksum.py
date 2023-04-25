import google_crc32c

from . import exceptions


def generate_checksum(data: bytes) -> int:
    """
    Calculates the CRC32C checksum of the provided data.
    Args:
        data: the bytes over which the checksum should be calculated.
    Returns:
        An int representing the CRC32C checksum of the provided bytes.
    """
    crc32c = google_crc32c.Checksum()
    crc32c.update(data)
    return int(crc32c.hexdigest(), 16)


def validate_checksum_or_exception(data: bytes, checksum: int) -> None:
    expected_checksum = generate_checksum(data=data)
    if checksum != expected_checksum:
        raise exceptions.InvalidChecksumError()
