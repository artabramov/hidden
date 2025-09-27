import unittest
import string
import jwt
import time
from unittest.mock import MagicMock, patch
from app.helpers.jwt_helper import (
    create_payload, generate_jti, encode_jwt, decode_jwt)


class JWTHelperTest(unittest.TestCase):

    def test_generate_jti_length_and_charset(self):
        length = 32
        result = generate_jti(length)
        self.assertEqual(len(result), length)
        allowed = set(string.ascii_letters + string.digits)
        self.assertTrue(set(result).issubset(allowed))

    def test_generate_jti_uniqueness(self):
        results = set()
        for _ in range(200):
            result = generate_jti(24)
            self.assertNotIn(result, results)
            results.add(result)

    @patch("app.helpers.jwt_helper.time")
    def test_create_payload_with_exp(self, time_mock):
        time_mock.time.return_value = 1756730933
        user_mock = MagicMock(id=1234, role="reader", username="johndoe")
        jti = "hUhnS4nB05g1up3zGz8o1riDGJoTlAbDeQPeb7Sz"
        exp = 2072253193

        result = create_payload(user_mock, jti, exp=exp)
        self.assertDictEqual(result, {
            "user_id": user_mock.id,
            "role": user_mock.role,
            "username": user_mock.username,
            "jti": jti,
            "exp": exp,
            "iat": time_mock.time.return_value
        })

    @patch("app.helpers.jwt_helper.time")
    def test_create_payload_without_exp(self, time_mock):
        time_mock.time.return_value = 1756730933
        user_mock = MagicMock(id=1234, role="reader", username="johndoe")
        jti = "hUhnS4nB05g1up3zGz8o1riDGJoTlAbDeQPeb7Sz"

        result = create_payload(user_mock, jti)
        self.assertDictEqual(result, {
            "user_id": user_mock.id,
            "role": user_mock.role,
            "username": user_mock.username,
            "jti": jti,
            "iat": time_mock.time.return_value
        })

    def test_decode_jwt_raises_on_immature_signature(self):
        secret, alg = "test-secret", "HS256"
        payload = {"sub": "1", "nbf": int(time.time()) + 60}
        token = jwt.encode(payload, secret, algorithm=alg)
        with self.assertRaises(jwt.ImmatureSignatureError):
            decode_jwt(token, secret, [alg])

    def test_decode_jwt_raises_on_future_iat(self):
        secret, alg = "test-secret", "HS256"
        payload = {"sub": "1", "iat": int(time.time()) + 60}
        token = jwt.encode(payload, secret, algorithm=alg)
        with self.assertRaises(jwt.ImmatureSignatureError):
            decode_jwt(token, secret, [alg])

    def test_decode_jwt_raises_on_non_integer_iat(self):
        secret, alg = "test-secret", "HS256"
        payload = {"sub": "1", "iat": "not-an-int"}
        token = jwt.encode(payload, secret, algorithm=alg)
        with self.assertRaises(jwt.InvalidIssuedAtError):
            decode_jwt(token, secret, [alg])

    def test_decode_jwt_raises_on_invalid_audience(self):
        secret, alg = "test-secret", "HS256"
        payload = {"sub": "1", "aud": "expected"}
        token = jwt.encode(payload, secret, algorithm=alg)
        with self.assertRaises(jwt.InvalidAudienceError):
            decode_jwt(token, secret, [alg])

    def test_decode_jwt_raises_on_expired(self):
        secret = "test-secret"
        alg = "HS256"
        payload = {"sub": "1", "exp": int(time.time()) - 10}
        token = jwt.encode(payload, secret, algorithm=alg)

        with self.assertRaises(jwt.ExpiredSignatureError):
            decode_jwt(token, secret, [alg])

    def test_decode_jwt_raises_on_invalid_signature(self):
        secret = "correct-secret"
        wrong_secret = "wrong-secret"
        alg = "HS256"
        payload = {"sub": "1", "exp": int(time.time()) + 60}
        token = jwt.encode(payload, wrong_secret, algorithm=alg)

        with self.assertRaises(jwt.InvalidSignatureError):
            decode_jwt(token, secret, [alg])

    def test_decode_jwt_raises_on_unsupported_algorithm(self):
        secret = "test-secret"
        token = jwt.encode({"sub": "1", "exp": int(time.time()) + 60},
                           secret, algorithm="HS512")

        with self.assertRaises(jwt.InvalidAlgorithmError):
            decode_jwt(token, secret, ["HS256"])

    def test_decode_jwt_raises_on_malformed_token(self):
        secret = "test-secret"
        algs = ["HS256"]
        malformed = "not.a.valid.jwt"

        with self.assertRaises(jwt.DecodeError):
            decode_jwt(malformed, secret, algs)

    def test_decode_jwt_raises_on_empty_algorithms_list(self):
        secret = "test-secret"
        payload = {"sub": "1"}
        token = encode_jwt(payload, secret, "HS256")
        with self.assertRaises(Exception):
            decode_jwt(token, secret, [])

    def test_encode_jwt_raises_on_unsupported_algorithm(self):
        secret = "test-secret"
        payload = {"sub": "1"}
        with self.assertRaises(NotImplementedError):
            encode_jwt(payload, secret, "HS1024")

    def test_encode_decode_roundtrip_without_exp(self):
        secret, alg = "test-secret", "HS256"
        payload = {"user_id": 42, "role": "reader", "jti": "abc",
                   "iat": int(time.time())}
        token = encode_jwt(payload, secret, alg)
        decoded = decode_jwt(token, secret, [alg])
        self.assertNotIn("exp", decoded)
        for k in ("user_id", "role", "jti", "iat"):
            self.assertEqual(decoded[k], payload[k])

    def test_encode_decode_roundtrip_with_exp_in_future(self):
        secret, alg = "test-secret", "HS256"
        payload = {"sub": "1", "exp": int(time.time()) + 60}
        token = encode_jwt(payload, secret, alg)
        decoded = decode_jwt(token, secret, [alg])
        self.assertEqual(decoded["sub"], "1")
