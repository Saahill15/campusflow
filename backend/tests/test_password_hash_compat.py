from services.auth_service import hash_password, verify_password


def test_hash_password_and_verify_normal_password():
    password = 'normal test password'
    hashed = hash_password(password)
    assert hashed
    assert verify_password(password, hashed) is True


def test_verify_existing_bcrypt_hash():
    password = 'another normal password'
    generated = hash_password(password)
    assert verify_password(password, generated) is True
