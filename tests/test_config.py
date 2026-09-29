import os
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from app.core.config import Settings


VALID_PRODUCTION_SETTINGS = {
    "ENVIRONMENT": "production",
    "SECRET_KEY": "production-signing-key-with-at-least-32-characters",
    "ADMIN_PASSWORD": "production-admin-password",
    "NEO4J_PASSWORD": "production-neo4j-password",
    "CORS_ORIGINS": "https://app.example.test,https://admin.example.test",
}


class SettingsTests(unittest.TestCase):
    def load_settings(self, values: dict[str, str] | None = None) -> Settings:
        with patch.dict(os.environ, values or {}, clear=True):
            return Settings(_env_file=None)

    def assert_invalid(self, values: dict[str, str]) -> None:
        with self.assertRaises(ValidationError):
            self.load_settings(values)

    def test_development_defaults_are_valid(self):
        settings = self.load_settings()

        self.assertEqual(settings.environment, "development")
        self.assertTrue(settings.cors_origin_list)

    def test_valid_production_configuration_loads(self):
        settings = self.load_settings(VALID_PRODUCTION_SETTINGS)

        self.assertEqual(settings.environment, "production")
        self.assertEqual(
            settings.cors_origin_list,
            ["https://app.example.test", "https://admin.example.test"],
        )

    def test_valid_staging_configuration_loads(self):
        settings = self.load_settings(
            VALID_PRODUCTION_SETTINGS | {"ENVIRONMENT": "staging"}
        )

        self.assertEqual(settings.environment, "staging")

    def test_staging_rejects_development_defaults(self):
        self.assert_invalid(
            VALID_PRODUCTION_SETTINGS
            | {
                "ENVIRONMENT": "staging",
                "ADMIN_PASSWORD": "admin123",
            }
        )

    def test_production_rejects_missing_secret_key(self):
        values = VALID_PRODUCTION_SETTINGS.copy()
        del values["SECRET_KEY"]

        self.assert_invalid(values)

    def test_production_rejects_weak_secret_key(self):
        values = VALID_PRODUCTION_SETTINGS | {"SECRET_KEY": "short-secret"}

        self.assert_invalid(values)

    def test_production_rejects_missing_admin_password(self):
        values = VALID_PRODUCTION_SETTINGS.copy()
        del values["ADMIN_PASSWORD"]

        self.assert_invalid(values)

    def test_production_rejects_development_admin_password(self):
        values = VALID_PRODUCTION_SETTINGS | {"ADMIN_PASSWORD": "admin123"}

        self.assert_invalid(values)

    def test_production_rejects_missing_neo4j_password(self):
        values = VALID_PRODUCTION_SETTINGS.copy()
        del values["NEO4J_PASSWORD"]

        self.assert_invalid(values)

    def test_production_rejects_development_neo4j_password(self):
        values = VALID_PRODUCTION_SETTINGS | {"NEO4J_PASSWORD": "password"}

        self.assert_invalid(values)

    def test_production_rejects_missing_cors_origins(self):
        values = VALID_PRODUCTION_SETTINGS.copy()
        del values["CORS_ORIGINS"]

        self.assert_invalid(values)

    def test_production_rejects_wildcard_or_localhost_cors_origins(self):
        self.assert_invalid(VALID_PRODUCTION_SETTINGS | {"CORS_ORIGINS": "*"})
        self.assert_invalid(
            VALID_PRODUCTION_SETTINGS | {"CORS_ORIGINS": "http://localhost:3000"}
        )


if __name__ == "__main__":
    unittest.main()
