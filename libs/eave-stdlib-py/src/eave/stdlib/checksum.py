from google.protobuf.wrappers_pb2 import Int64Value
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


def validate_checksum_or_exception(data: bytes, checksum: int | Int64Value) -> None:
    """
    Google KMS protobufs deliver the checksum value as an Int64Value type, but the runtime treats it as an int.
    The Int64Value parameter type here is mostly for the static type checker.
    """
    expected_checksum = generate_checksum(data=data)
    if checksum != expected_checksum:
        raise exceptions.InvalidChecksumError()
