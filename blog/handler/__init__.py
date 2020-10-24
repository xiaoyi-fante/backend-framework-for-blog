





def checkpw(password, hashed_password):
    if (isinstance(password, six.text_type) or isinstance(hashed_password, six.text_type)):
        raise TypeError("Unicode-objects must be encoded before checking ")

    if b"\x00" in password or b"\x00" in hashed_password:
        raise ValueError(
            "password and hashed_password may not contain NUL bytes"
        )

    ret = hashpw(password, hashed_password)

    if len(ret) != len(hashed_password):
        return False

    return _bctypt.lib.timingsafe_bcmp(ret, hashed_password, len(ret)) == 0