# tests/runtime/test_passphrase.py
# SPDX-License-Identifier: GPL-3.0-only

import io
import os
import sys
import unittest
from unittest.mock import mock_open, patch

from app.runtime import passphrase as pp


class TestPrintDecryptValueError(unittest.TestCase):
    def _stderr_for(self, exc: ValueError) -> str:
        buf = io.StringIO()
        with patch.object(sys, "stderr", buf):
            pp._print_decrypt_value_error(exc)
        return buf.getvalue()

    def test_invalid_password_message(self):
        out = self._stderr_for(
            ValueError("invalid password or corrupted data"),
        )
        self.assertIn("wrong password", out)

    def test_ciphertext_too_short(self):
        out = self._stderr_for(ValueError("ciphertext too short"))
        self.assertIn("too small", out)

    def test_invalid_magic(self):
        out = self._stderr_for(ValueError("invalid magic"))
        self.assertIn("does not look like", out)

    def test_unsupported_version(self):
        out = self._stderr_for(ValueError("unsupported version"))
        self.assertIn("unsupported format version", out)

    def test_generic_message(self):
        out = self._stderr_for(ValueError("other reason"))
        self.assertIn("other reason", out)


class TestMain(unittest.TestCase):
    def test_read_error_returns_1(self):
        def boom(*_a, **_k):
            raise OSError("nope")

        with patch("builtins.open", boom):
            rc = pp.main(["/missing.enc"])

        self.assertEqual(rc, 1)

    def test_decrypt_failure_returns_1(self):
        m_open = mock_open(read_data=b"blob")
        err = io.StringIO()

        with (
            patch("builtins.open", m_open),
            patch(
                "app.runtime.passphrase.getpass.getpass",
                return_value="pw",
            ),
            patch(
                "app.runtime.passphrase.decrypt_passphrase",
                side_effect=ValueError("invalid magic"),
            ),
            patch.object(sys, "stderr", err),
        ):
            rc = pp.main(["/x.enc"])

        self.assertEqual(rc, 1)
        self.assertIn("does not look like", err.getvalue())

    def test_success_writes_plaintext(self):
        m_open = mock_open(read_data=b"blob")
        out_buf = io.BytesIO()

        class _Stdout:
            def isatty(self) -> bool:
                return False

            @property
            def buffer(self) -> io.BytesIO:
                return out_buf

        fake_out = _Stdout()

        with (
            patch("builtins.open", m_open),
            patch(
                "app.runtime.passphrase.getpass.getpass",
                return_value="pw",
            ),
            patch(
                "app.runtime.passphrase.decrypt_passphrase",
                return_value=b"plain-bytes",
            ),
            patch("app.runtime.passphrase.sys.stdout", fake_out),
        ):
            rc = pp.main(["/x.enc"])

        self.assertEqual(rc, 0)
        self.assertEqual(out_buf.getvalue(), b"plain-bytes")

    def test_tty_adds_newline(self):
        m_open = mock_open(read_data=b"blob")
        out_buf = io.BytesIO()

        class _Stdout:
            def isatty(self) -> bool:
                return True

            @property
            def buffer(self) -> io.BytesIO:
                return out_buf

        with (
            patch("builtins.open", m_open),
            patch(
                "app.runtime.passphrase.getpass.getpass",
                return_value="pw",
            ),
            patch(
                "app.runtime.passphrase.decrypt_passphrase",
                return_value=b"x",
            ),
            patch("app.runtime.passphrase.sys.stdout", _Stdout()),
        ):
            rc = pp.main(["/x.enc"])

        self.assertEqual(rc, 0)
        self.assertTrue(out_buf.getvalue().endswith(b"\n"))

    def test_read_error_writes_message_to_stderr(self):
        err = io.StringIO()

        def boom(*_a, **_k):
            raise OSError("nope")

        with (
            patch("builtins.open", boom),
            patch.object(sys, "stderr", err),
        ):
            rc = pp.main(["/missing.enc"])

        self.assertEqual(rc, 1)
        self.assertIn("Could not read file: nope", err.getvalue())

    def test_open_called_in_binary_mode(self):
        m_open = mock_open(read_data=b"blob")
        out_buf = io.BytesIO()

        class _Stdout:
            def isatty(self) -> bool:
                return False

            @property
            def buffer(self) -> io.BytesIO:
                return out_buf

        with (
            patch("builtins.open", m_open),
            patch(
                "app.runtime.passphrase.getpass.getpass",
                return_value="pw",
            ),
            patch(
                "app.runtime.passphrase.decrypt_passphrase",
                return_value=b"plain",
            ),
            patch("app.runtime.passphrase.sys.stdout", _Stdout()),
        ):
            rc = pp.main(["/x.enc"])

        self.assertEqual(rc, 0)
        m_open.assert_called_once_with("/x.enc", "rb")

    def test_password_is_encoded_and_passed_to_decrypt(self):
        m_open = mock_open(read_data=b"blob")
        out_buf = io.BytesIO()

        class _Stdout:
            def isatty(self) -> bool:
                return False

            @property
            def buffer(self) -> io.BytesIO:
                return out_buf

        with (
            patch("builtins.open", m_open),
            patch(
                "app.runtime.passphrase.getpass.getpass",
                return_value="päss",
            ) as mock_getpass,
            patch(
                "app.runtime.passphrase.decrypt_passphrase",
                return_value=b"plain",
            ) as mock_decrypt,
            patch("app.runtime.passphrase.sys.stdout", _Stdout()),
        ):
            rc = pp.main(["/x.enc"])

        self.assertEqual(rc, 0)
        mock_getpass.assert_called_once_with("Enter master password: ")
        mock_decrypt.assert_called_once_with(
            b"blob",
            "päss".encode("utf-8"),
        )

    def test_decrypt_failure_calls_error_mapper(self):
        m_open = mock_open(read_data=b"blob")
        exc = ValueError("invalid magic")

        with (
            patch("builtins.open", m_open),
            patch(
                "app.runtime.passphrase.getpass.getpass",
                return_value="pw",
            ),
            patch(
                "app.runtime.passphrase.decrypt_passphrase",
                side_effect=exc,
            ),
            patch(
                "app.runtime.passphrase._print_decrypt_value_error",
            ) as mock_print_error,
        ):
            rc = pp.main(["/x.enc"])

        self.assertEqual(rc, 1)
        mock_print_error.assert_called_once_with(exc)

    def test_success_does_not_add_newline_when_not_tty(self):
        m_open = mock_open(read_data=b"blob")
        out_buf = io.BytesIO()

        class _Stdout:
            def isatty(self) -> bool:
                return False

            @property
            def buffer(self) -> io.BytesIO:
                return out_buf

        with (
            patch("builtins.open", m_open),
            patch(
                "app.runtime.passphrase.getpass.getpass",
                return_value="pw",
            ),
            patch(
                "app.runtime.passphrase.decrypt_passphrase",
                return_value=b"x",
            ),
            patch("app.runtime.passphrase.sys.stdout", _Stdout()),
        ):
            rc = pp.main(["/x.enc"])

        self.assertEqual(rc, 0)
        self.assertEqual(out_buf.getvalue(), b"x")

    def test_main_without_args_uses_install_secrets_dir_env(self):
        blob = b"blob"
        plaintext = b"passphrase"
        stderr = io.StringIO()

        with (
            patch.dict(
                "os.environ",
                {"INSTALL_SECRETS_DIR": "/secrets"},
                clear=False,
            ),
            patch(
                "builtins.open",
                mock_open(read_data=blob),
            ) as mock_file,
            patch(
                "app.runtime.passphrase.getpass.getpass",
                return_value="pw",
            ),
            patch(
                "app.runtime.passphrase.decrypt_passphrase",
                return_value=plaintext,
            ),
            patch(
                "app.runtime.passphrase.sys.stdout",
                type("_Stdout", (), {
                    "buffer": type("_Buf", (), {
                        "write": lambda self, b: None,
                    })(),
                    "isatty": lambda self: False,
                })(),
            ),
            patch.object(sys, "stderr", stderr),
        ):
            rc = pp.main([])

        self.assertEqual(rc, 0)
        mock_file.assert_called_once_with(
            "/secrets/gocryptfs_passphrase.enc", "rb"
        )

    def test_main_without_args_and_no_env_returns_1(self):
        stderr = io.StringIO()

        env_without_secrets = {
            k: v for k, v in os.environ.items()
            if k != "INSTALL_SECRETS_DIR"
        }
        with (
            patch.dict("os.environ", env_without_secrets, clear=True),
            patch.object(sys, "stderr", stderr),
        ):
            rc = pp.main([])

        self.assertEqual(rc, 1)
        self.assertIn("INSTALL_SECRETS_DIR", stderr.getvalue())

    def test_help_raises_system_exit_and_shows_epilog(self):
        stdout = io.StringIO()

        with patch.object(sys, "stdout", stdout):
            with self.assertRaises(SystemExit) as ctx:
                pp.main(["-h"])

        self.assertEqual(ctx.exception.code, 0)
        text = stdout.getvalue()
        self.assertIn("Decrypt key material with a password", text)
        self.assertIn("Emergency decryption", text)
        self.assertIn("python3 -m app.runtime.passphrase", text)
