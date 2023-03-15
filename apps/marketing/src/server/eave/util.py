import google_crc32c


def crc32c(data: bytes) -> int:
    crc32c = google_crc32c.Checksum()
    crc32c.update(data)
    return int(crc32c.hexdigest(), 16)
