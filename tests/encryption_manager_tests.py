import unittest
import os
from cryptography.exceptions import InvalidTag
from app.managers.encryption_manager import EncryptionManager


class _CfgHKDF:
    CRYPTO_KEY_LENGTH = 32
    CRYPTO_NONCE_LENGTH = 12
    CRYPTO_HKDF_INFO = b"aesgcm-v1"
    CRYPTO_HKDF_SALT_B64 = None
    CRYPTO_DERIVE_WITH_HKDF = True
    CRYPTO_DEFAULT_ENCODING = "utf-8"
    CRYPTO_AAD_DEFAULT = None


class _CfgHKDF_WithAAD(_CfgHKDF):
    CRYPTO_AAD_DEFAULT = b"env=prod"


class _CfgHKDF_WithSalt(_CfgHKDF):
    CRYPTO_HKDF_SALT_B64 = "c2FsdHNhbHRzYWx0c2FsdA=="


class _CfgHKDF_WithDifferentInfo(_CfgHKDF):
    CRYPTO_HKDF_INFO = b"aesgcm-v2"


class _CfgRawKey(_CfgHKDF):
    CRYPTO_DERIVE_WITH_HKDF = False


class EncryptionManagerExtendedTest(unittest.TestCase):

    def test_init_bytes_vs_str_secret_equivalent(self):
        cfg = _CfgHKDF()
        a = EncryptionManager(cfg, "abc")
        b = EncryptionManager(cfg, b"abc")

        t1 = a.encrypt_str("x")
        self.assertEqual(b.decrypt_str(t1), "x")

        t2 = b.encrypt_str("y")
        self.assertEqual(a.decrypt_str(t2), "y")

        self.assertEqual(a.get_hash("payload"), b.get_hash("payload"))

    def test_init_invalid_salt_base64_raises(self):
        class _Cfg(_CfgHKDF): CRYPTO_HKDF_SALT_B64 = "%%%not-base64%%%"
        with self.assertRaises(Exception):
            EncryptionManager(_Cfg(), "s")

    def test_init_raw_key_bytes_lengths_ok(self):
        for n in (16, 24, 32):
            class _Cfg(_CfgRawKey): CRYPTO_KEY_LENGTH = n
            EncryptionManager(_Cfg(), b"\x00" * n)

    def test_init_raw_key_invalid_lengths_raise(self):
        class _Cfg(_CfgRawKey): CRYPTO_KEY_LENGTH = 48
        with self.assertRaises(ValueError):
            EncryptionManager(_Cfg(), "X" * 48)

    def test_init_raw_key_accepts_valid_lengths(self):
        for key_len in (16, 24, 32):
            class _Cfg(_CfgRawKey):
                CRYPTO_KEY_LENGTH = key_len
            secret = "X" * key_len
            em = EncryptionManager(_Cfg(), secret)
            pt = b"abc"
            ct = em.encrypt_bytes(pt)
            self.assertEqual(em.decrypt_bytes(ct), pt)

    def test_init_raw_key_wrong_length_raises(self):
        cfg = _CfgRawKey()
        with self.assertRaises(ValueError):
            EncryptionManager(cfg, "short")

    def test_encrypt_bytes_roundtrip_hkdf(self):
        cfg = _CfgHKDF()
        a = EncryptionManager(cfg, "topsecret")
        b = EncryptionManager(cfg, "topsecret")
        pt = b"The quick brown fox"
        ct1 = a.encrypt_bytes(pt)
        ct2 = a.encrypt_bytes(pt)
        self.assertIsInstance(ct1, (bytes, bytearray))
        self.assertNotEqual(ct1, ct2)
        self.assertEqual(b.decrypt_bytes(ct1), pt)
        self.assertEqual(b.decrypt_bytes(ct2), pt)

    def test_encrypt_bytes_ciphertext_length_formula(self):
        cfg = _CfgHKDF()
        em = EncryptionManager(cfg, "LENGTH-CHECK")
        for n in (0, 1, 15, 16, 31, 32, 1024):
            pt = os.urandom(n)
            ct = em.encrypt_bytes(pt)
            self.assertEqual(len(ct), cfg.CRYPTO_NONCE_LENGTH + n + 16)

    def test_encrypt_bytes_empty_plaintext_roundtrip(self):
        em = EncryptionManager(_CfgHKDF(), "s")
        ct = em.encrypt_bytes(b"")
        self.assertEqual(em.decrypt_bytes(ct), b"")

    def test_encrypt_bytes_large_payload_roundtrip(self):
        cfg = _CfgHKDF()
        em = EncryptionManager(cfg, "BIG-SECRET")
        data = os.urandom(256 * 1024)
        ct = em.encrypt_bytes(data)
        self.assertEqual(em.decrypt_bytes(ct), data)

    def test_encrypt_bytes_accepts_nonstandard_nonce_len(self):
        class _Cfg(_CfgHKDF): CRYPTO_NONCE_LENGTH = 8
        em1 = EncryptionManager(_Cfg(), "s")
        em2 = EncryptionManager(_Cfg(), "s")

        pt = b"x"
        ct = em1.encrypt_bytes(pt)

        self.assertEqual(len(ct), 8 + len(pt) + 16)
        self.assertEqual(em2.decrypt_bytes(ct), pt)

    def test_encrypt_bytes_nonce_randomness_uniqueness(self):
        cfg = _CfgHKDF()
        em = EncryptionManager(cfg, "NONCE-SECRET")
        nonces = set()
        for _ in range(64):
            ct = em.encrypt_bytes(b"x")
            nonces.add(ct[:cfg.CRYPTO_NONCE_LENGTH])
        self.assertEqual(len(nonces), 64)

    def test_encrypt_bool_roundtrip_true_false(self):
        em = EncryptionManager(_CfgHKDF(), "BOOL-SECRET")
        for v in (True, False):
            token = em.encrypt_bool(v)
            self.assertIsInstance(token, str)
            self.assertEqual(em.decrypt_bool(token), v)

    def test_encrypt_bool_token_decodes_to_int_values(self):
        em = EncryptionManager(_CfgHKDF(), "BOOL-SECRET")
        self.assertEqual(em.decrypt_int(em.encrypt_bool(True)), 1)
        self.assertEqual(em.decrypt_int(em.encrypt_bool(False)), 0)

    def test_encrypt_int_roundtrip_negative_and_big(self):
        em = EncryptionManager(_CfgHKDF(), "s")
        for v in (-1, 0, 2**63, 2**80):
            self.assertEqual(em.decrypt_int(em.encrypt_int(v)), v)

    def test_encrypt_str_unicode_roundtrip(self):
        cfg = _CfgHKDF()
        em = EncryptionManager(cfg, "UNICODE-SECRET")
        s = "Привет, мир! — 你好，世界 — ¿Qué tal?"
        token = em.encrypt_str(s)
        self.assertIsInstance(token, str)
        self.assertEqual(em.decrypt_str(token), s)

    def test_encrypt_str_empty_and_whitespace_roundtrip(self):
        cfg = _CfgHKDF()
        em = EncryptionManager(cfg, "STR-SECRET")
        for s in ("", " ", "\t\n"):
            token = em.encrypt_str(s)
            self.assertEqual(em.decrypt_str(token), s)

    def test_encrypt_decrypt_none_passthrough(self):
        cfg = _CfgHKDF()
        em = EncryptionManager(cfg, "NONE-SECRET")
        self.assertIsNone(em.encrypt_bytes(None))
        self.assertIsNone(em.decrypt_bytes(None))
        self.assertIsNone(em.encrypt_str(None))
        self.assertIsNone(em.decrypt_str(None))
        self.assertIsNone(em.encrypt_int(None))
        self.assertIsNone(em.decrypt_int(None))
        self.assertIsNone(em.encrypt_bool(None))
        self.assertIsNone(em.decrypt_bool(None))

    def test_decrypt_bool_truthiness_for_nonzero_int(self):
        em = EncryptionManager(_CfgHKDF(), "s")
        tok = em.encrypt_int(2)
        self.assertTrue(em.decrypt_bool(tok))

    def test_decrypt_bool_invalid_token_raises(self):
        em = EncryptionManager(_CfgHKDF(), "s")
        with self.assertRaises(Exception):
            em.decrypt_bool("$$$not-base64$$$")

    def test_decrypt_bytes_tamper_ciphertext_fails(self):
        cfg = _CfgHKDF()
        em = EncryptionManager(cfg, "TAMPER-SECRET")
        pt = b"data"
        ct = em.encrypt_bytes(pt)
        tampered = bytearray(ct)
        nonce_len = cfg.CRYPTO_NONCE_LENGTH
        tampered[nonce_len] ^= 0x01
        with self.assertRaises(InvalidTag):
            em.decrypt_bytes(bytes(tampered))

    def test_decrypt_bytes_exact_nonce_length_raises(self):
        em = EncryptionManager(_CfgHKDF(), "s")
        ct = em.encrypt_bytes(b"d")
        with self.assertRaises(Exception):
            em.decrypt_bytes(ct[:_CfgHKDF.CRYPTO_NONCE_LENGTH])

    def test_decrypt_bytes_aad_mismatch_fails(self):
        cfg_with_aad = _CfgHKDF_WithAAD()
        cfg_no_aad = _CfgHKDF()
        a = EncryptionManager(cfg_with_aad, "aad-secret")
        b = EncryptionManager(cfg_no_aad, "aad-secret")
        ct = a.encrypt_bytes(b"bound")
        with self.assertRaises(InvalidTag):
            b.decrypt_bytes(ct)

    def test_decrypt_bytes_hkdf_salt_incompatibility(self):
        cfg1 = _CfgHKDF_WithSalt()
        cfg2 = _CfgHKDF()
        a = EncryptionManager(cfg1, "salted")
        b = EncryptionManager(cfg2, "salted")
        ct = a.encrypt_bytes(b"msg")
        with self.assertRaises(InvalidTag):
            b.decrypt_bytes(ct)

    def test_decrypt_bytes_hkdf_info_incompatibility(self):
        cfg1 = _CfgHKDF()
        cfg2 = _CfgHKDF_WithDifferentInfo()
        a = EncryptionManager(cfg1, "info-secret")
        b = EncryptionManager(cfg2, "info-secret")
        ct = a.encrypt_bytes(b"msg")
        with self.assertRaises(InvalidTag):
            b.decrypt_bytes(ct)

    def test_decrypt_bytes_aad_mismatch_raises(self):
        class _C1(_CfgHKDF): CRYPTO_AAD_DEFAULT = b"env=one"
        class _C2(_CfgHKDF): CRYPTO_AAD_DEFAULT = b"env=two"
        a = EncryptionManager(_C1(), "s")
        b = EncryptionManager(_C2(), "s")
        ct = a.encrypt_bytes(b"d")
        with self.assertRaises(InvalidTag):
            b.decrypt_bytes(ct)

    def test_decrypt_bytes_with_truncated_payload_raises(self):
        cfg = _CfgHKDF()
        em = EncryptionManager(cfg, "TRUNCATE")
        ct = em.encrypt_bytes(b"123456")
        for cut in (1, 5, cfg.CRYPTO_NONCE_LENGTH + 1, len(ct) - 1):
            with self.assertRaises(Exception):
                em.decrypt_bytes(ct[:cut])

    def test_decrypt_bool_from_int_token_zero_and_nonzero(self):
        em = EncryptionManager(_CfgHKDF(), "BOOL-SECRET")
        tok_true = em.encrypt_int(5)
        tok_false = em.encrypt_int(0)
        self.assertTrue(em.decrypt_bool(tok_true))
        self.assertFalse(em.decrypt_bool(tok_false))

    def test_decrypt_bool_invalid_token_raises(self):
        em = EncryptionManager(_CfgHKDF(), "BOOL-SECRET")
        with self.assertRaises(Exception):
            em.decrypt_bool("$$$not-base64$$$")

    def test_decrypt_int_invalid_token_raises(self):
        cfg = _CfgHKDF()
        em = EncryptionManager(cfg, "INT-SECRET")
        with self.assertRaises(Exception):
            em.decrypt_int("$$$not-base64$$$")
        bad = em.encrypt_str("not-an-int")
        with self.assertRaises(ValueError):
            em.decrypt_int(bad)

    def test_decrypt_str_wrong_secret_fails(self):
        cfg = _CfgHKDF()
        a = EncryptionManager(cfg, "secret-A")
        b = EncryptionManager(cfg, "secret-B")
        token = a.encrypt_str("hello")
        with self.assertRaises(InvalidTag):
            b.decrypt_str(token)

    def test_decrypt_str_invalid_base64_raises(self):
        em = EncryptionManager(_CfgHKDF(), "s")
        with self.assertRaises(Exception):
            em.decrypt_str("**not-base64**")

    def test_get_hash_deterministic_and_hex(self):
        em = EncryptionManager(_CfgHKDF(), "super-secret")
        h1 = em.get_hash("payload")
        h2 = em.get_hash("payload")
        self.assertEqual(h1, h2)
        self.assertIsInstance(h1, str)
        self.assertEqual(len(h1), 128)
        int(h1, 16)

    def test_get_hash_changes_with_value_and_secret(self):
        a = EncryptionManager(_CfgHKDF(), "secret-A")
        b = EncryptionManager(_CfgHKDF(), "secret-B")
        self.assertNotEqual(a.get_hash("data"), b.get_hash("data"))
        em = EncryptionManager(_CfgHKDF(), "secret")
        self.assertNotEqual(em.get_hash("data-1"), em.get_hash("data-2"))

    def test_get_hash_handles_unicode_and_empty(self):
        em = EncryptionManager(_CfgHKDF(), "секрет")
        self.assertEqual(len(em.get_hash("")), 128)
        text = "Hello world!"
        self.assertEqual(len(em.get_hash(text)), 128)

    def test_get_hash_deterministic_and_hex_length(self):
        em = EncryptionManager(_CfgHKDF(), "super-secret")
        d1 = em.get_hash("payload")
        d2 = em.get_hash("payload")
        self.assertEqual(d1, d2)
        self.assertIsInstance(d1, str)
        self.assertEqual(len(d1), 128)
        int(d1, 16)

    def test_get_hash_changes_with_value_and_secret_again(self):
        a = EncryptionManager(_CfgHKDF(), "secret-A")
        b = EncryptionManager(_CfgHKDF(), "secret-B")
        self.assertNotEqual(a.get_hash("data"), b.get_hash("data"))
        em = EncryptionManager(_CfgHKDF(), "secret")
        self.assertNotEqual(em.get_hash("data-1"), em.get_hash("data-2"))

    def test_get_hash_handles_unicode_and_empty_extended(self):
        em = EncryptionManager(_CfgHKDF(), "секрет")
        self.assertEqual(len(em.get_hash("")), 128)
        txt = "Привет, мир! — 你好，世界 — ¿Qué tal?"
        self.assertEqual(len(em.get_hash(txt)), 128)

    def test_get_hash_independent_of_crypto_info(self):
        s = "same-secret"
        cfg1 = _CfgHKDF()
        cfg2 = _CfgHKDF_WithDifferentInfo()
        h1 = EncryptionManager(cfg1, s).get_hash("msg")
        h2 = EncryptionManager(cfg2, s).get_hash("msg")
        self.assertEqual(h1, h2)

    def test_get_hash_changes_with_salt(self):
        s = "salted-secret"
        cfg_no_salt = _CfgHKDF()
        cfg_with_salt = _CfgHKDF_WithSalt()
        h1 = EncryptionManager(cfg_no_salt, s).get_hash("msg")
        h2 = EncryptionManager(cfg_with_salt, s).get_hash("msg")
        self.assertNotEqual(h1, h2)

    def test_get_hash_raw_mode(self):
        em1 = EncryptionManager(_CfgRawKey(), "X" * 32)
        em2 = EncryptionManager(_CfgRawKey(), "Y" * 32)
        d1 = em1.get_hash("abc")
        d2 = em1.get_hash("abc")
        d3 = em2.get_hash("abc")
        self.assertEqual(d1, d2)
        self.assertNotEqual(d1, d3)

    def test_get_hash_accepts_binary_secret(self):
        cfg = _CfgHKDF()
        secret_bytes = os.urandom(40)
        em = EncryptionManager(cfg, secret_bytes)
        d = em.get_hash("bin")
        self.assertEqual(len(d), 128)
        int(d, 16)
