"""
Extended comprehensive tests for src/auth.py to achieve 90%+ coverage.

This test suite focuses on:
1. get_public_key() edge cases (caching, database errors, parsing)
2. get_current_user() security edge cases (missing sub claim, user not found)
3. JWT validation error scenarios (expired tokens, invalid signatures, wrong issuer)
4. Attack scenarios (token tampering, malformed headers)

Target: Increase coverage from 69.84% to 90%+
Missing lines: 54-85 (get_public_key), 134, 150 (get_current_user)
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user, get_public_key, ISSUER, AUDIENCE, _public_key_cache


class TestGetPublicKeyFunction:
    """Test suite for get_public_key() function - Lines 54-85."""

    @pytest.mark.asyncio
    async def test_get_public_key_from_database_pem_format(self, test_session: AsyncSession):
        """Test fetching PEM-formatted public key from database."""
        # Clear cache before test
        import src.auth
        src.auth._public_key_cache = None

        # Mock database response with PEM format
        with patch.object(test_session, "execute", new_callable=AsyncMock) as mock_execute:
            mock_result = MagicMock()
            mock_row = ("-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...",)
            mock_result.fetchone.return_value = mock_row
            mock_execute.return_value = mock_result

            # Execute
            public_key = await get_public_key(test_session)

            # Assert
            assert isinstance(public_key, str)
            assert public_key.startswith("-----BEGIN PUBLIC KEY-----")
            mock_execute.assert_called_once()

        # Clean up
        src.auth._public_key_cache = None

    @pytest.mark.asyncio
    async def test_get_public_key_from_database_jwk_format(self, test_session: AsyncSession):
        """Test fetching JWK-formatted public key from database."""
        # Clear cache before test
        import src.auth
        src.auth._public_key_cache = None

        # Mock database response with JWK format
        jwk_dict = {
            "kty": "OKP",
            "crv": "Ed25519",
            "x": "11qYAYKxCrfVS_7TyWQHOg7hcvPapiMlrwIaaPcHURo"
        }

        with patch.object(test_session, "execute", new_callable=AsyncMock) as mock_execute:
            mock_result = MagicMock()
            mock_row = (json.dumps(jwk_dict),)
            mock_result.fetchone.return_value = mock_row
            mock_execute.return_value = mock_result

            # Execute
            public_key = await get_public_key(test_session)

            # Assert - should add alg field for Ed25519 keys
            assert isinstance(public_key, dict)
            assert public_key["kty"] == "OKP"
            assert public_key["crv"] == "Ed25519"
            assert public_key["alg"] == "EdDSA"  # Auto-added for Ed25519

        # Clean up
        src.auth._public_key_cache = None

    @pytest.mark.asyncio
    async def test_get_public_key_jwk_without_alg_auto_adds_eddsa(self, test_session: AsyncSession):
        """Test that Ed25519 JWK without alg field gets EdDSA added automatically."""
        # Clear cache before test
        import src.auth
        src.auth._public_key_cache = None

        jwk_without_alg = {
            "kty": "OKP",
            "crv": "Ed25519",
            "x": "test_key_data"
        }

        with patch.object(test_session, "execute", new_callable=AsyncMock) as mock_execute:
            mock_result = MagicMock()
            mock_row = (json.dumps(jwk_without_alg),)
            mock_result.fetchone.return_value = mock_row
            mock_execute.return_value = mock_result

            # Execute
            public_key = await get_public_key(test_session)

            # Assert
            assert public_key["alg"] == "EdDSA"

        # Clean up
        src.auth._public_key_cache = None

    @pytest.mark.asyncio
    async def test_get_public_key_caching_behavior(self, test_session: AsyncSession):
        """Test that public key is cached after first fetch."""
        # Clear cache before test
        import src.auth
        src.auth._public_key_cache = None

        jwk_dict = {"kty": "OKP", "crv": "Ed25519", "x": "test", "alg": "EdDSA"}

        with patch.object(test_session, "execute", new_callable=AsyncMock) as mock_execute:
            mock_result = MagicMock()
            mock_row = (json.dumps(jwk_dict),)
            mock_result.fetchone.return_value = mock_row
            mock_execute.return_value = mock_result

            # First call - should hit database
            key1 = await get_public_key(test_session)
            assert mock_execute.call_count == 1

            # Second call - should use cache, not hit database again
            key2 = await get_public_key(test_session)
            assert mock_execute.call_count == 1  # Still 1, not 2
            assert key1 == key2

            # Verify cache is populated
            assert src.auth._public_key_cache is not None

        # Clean up cache
        src.auth._public_key_cache = None

    @pytest.mark.asyncio
    async def test_get_public_key_returns_cached_value_immediately(self, test_session: AsyncSession):
        """Test that cached key is returned without database query."""
        import src.auth

        # Pre-populate cache
        cached_key = {"kty": "OKP", "crv": "Ed25519", "alg": "EdDSA", "x": "cached"}
        src.auth._public_key_cache = cached_key

        with patch.object(test_session, "execute", new_callable=AsyncMock) as mock_execute:
            # Execute
            result = await get_public_key(test_session)

            # Assert - should NOT call database
            mock_execute.assert_not_called()
            assert result == cached_key

        # Clean up
        src.auth._public_key_cache = None

    @pytest.mark.asyncio
    async def test_get_public_key_no_key_in_database(self, test_session: AsyncSession):
        """Test error when no public key exists in database."""
        import src.auth
        src.auth._public_key_cache = None

        with patch.object(test_session, "execute", new_callable=AsyncMock) as mock_execute:
            mock_result = MagicMock()
            mock_result.fetchone.return_value = None  # No key found
            mock_execute.return_value = mock_result

            # Execute & Assert
            with pytest.raises(HTTPException) as exc_info:
                await get_public_key(test_session)

            assert exc_info.value.status_code == 500
            assert "No public key found" in exc_info.value.detail
            assert "Better Auth" in exc_info.value.detail

        src.auth._public_key_cache = None

    @pytest.mark.asyncio
    async def test_get_public_key_invalid_json_fallback_to_string(self, test_session: AsyncSession):
        """Test that invalid JSON falls back to treating key as raw string (PEM)."""
        import src.auth
        src.auth._public_key_cache = None

        # Invalid JSON that will fail to parse
        invalid_json = "not-valid-json-{{"

        with patch.object(test_session, "execute", new_callable=AsyncMock) as mock_execute:
            mock_result = MagicMock()
            mock_row = (invalid_json,)
            mock_result.fetchone.return_value = mock_row
            mock_execute.return_value = mock_result

            # Execute
            public_key = await get_public_key(test_session)

            # Assert - should fallback to raw string
            assert isinstance(public_key, str)
            assert public_key == invalid_json

        src.auth._public_key_cache = None

    @pytest.mark.asyncio
    async def test_get_public_key_jwk_with_existing_alg_preserved(self, test_session: AsyncSession):
        """Test that JWK with existing alg field is preserved."""
        import src.auth
        src.auth._public_key_cache = None

        jwk_with_alg = {
            "kty": "RSA",
            "alg": "RS256",
            "n": "test_modulus",
            "e": "AQAB"
        }

        with patch.object(test_session, "execute", new_callable=AsyncMock) as mock_execute:
            mock_result = MagicMock()
            mock_row = (json.dumps(jwk_with_alg),)
            mock_result.fetchone.return_value = mock_row
            mock_execute.return_value = mock_result

            # Execute
            public_key = await get_public_key(test_session)

            # Assert - alg should remain RS256, not changed to EdDSA
            assert public_key["alg"] == "RS256"

        src.auth._public_key_cache = None


class TestGetCurrentUserSecurityEdgeCases:
    """Test suite for get_current_user() security edge cases - Lines 134, 150."""

    @pytest.mark.asyncio
    async def test_get_current_user_missing_sub_claim(self, test_session: AsyncSession):
        """Test that missing 'sub' claim raises 401 (Line 134)."""
        # Payload without 'sub' claim
        payload = {
            "email": "test@example.com",
            "iss": ISSUER,
            "aud": AUDIENCE,
        }

        mock_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="mock-token")

        with patch("src.auth.get_public_key", new_callable=AsyncMock) as mock_get_key:
            mock_get_key.return_value = {"kty": "OKP", "crv": "Ed25519", "alg": "EdDSA"}

            with patch("jwt.PyJWK") as mock_pyjwk:
                mock_key_instance = MagicMock()
                mock_key_instance.key = "mock-key"
                mock_pyjwk.return_value = mock_key_instance

                with patch("jwt.decode") as mock_decode:
                    mock_decode.return_value = payload  # No 'sub' claim

                    # Execute & Assert
                    with pytest.raises(HTTPException) as exc_info:
                        await get_current_user(mock_creds, test_session)

                    assert exc_info.value.status_code == 401
                    assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_sub_is_none(self, test_session: AsyncSession):
        """Test that 'sub' claim with None value raises 401."""
        payload = {
            "sub": None,  # Explicitly None
            "email": "test@example.com",
            "iss": ISSUER,
            "aud": AUDIENCE,
        }

        mock_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="mock-token")

        with patch("src.auth.get_public_key", new_callable=AsyncMock) as mock_get_key:
            mock_get_key.return_value = {"kty": "OKP", "crv": "Ed25519", "alg": "EdDSA"}

            with patch("jwt.PyJWK") as mock_pyjwk:
                mock_key_instance = MagicMock()
                mock_key_instance.key = "mock-key"
                mock_pyjwk.return_value = mock_key_instance

                with patch("jwt.decode") as mock_decode:
                    mock_decode.return_value = payload

                    with pytest.raises(HTTPException) as exc_info:
                        await get_current_user(mock_creds, test_session)

                    assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found_in_database(self, test_session: AsyncSession):
        """Test that user not existing in database raises 401 (Line 150)."""
        user_id = "nonexistent-user-id"
        payload = {
            "sub": user_id,
            "email": "test@example.com",
            "iss": ISSUER,
            "aud": AUDIENCE,
        }

        mock_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-token")

        with patch("src.auth.get_public_key", new_callable=AsyncMock) as mock_get_key:
            mock_get_key.return_value = {"kty": "OKP", "crv": "Ed25519", "alg": "EdDSA"}

            with patch("jwt.PyJWK") as mock_pyjwk:
                mock_key_instance = MagicMock()
                mock_key_instance.key = "mock-key"
                mock_pyjwk.return_value = mock_key_instance

                with patch("jwt.decode") as mock_decode:
                    mock_decode.return_value = payload

                    # Mock session.get to return None (user not found)
                    with patch.object(test_session, "get", new_callable=AsyncMock) as mock_get:
                        mock_get.return_value = None

                        # Execute & Assert
                        with pytest.raises(HTTPException) as exc_info:
                            await get_current_user(mock_creds, test_session)

                        assert exc_info.value.status_code == 401
                        assert "Could not validate credentials" in exc_info.value.detail
                        mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_current_user_user_deleted_from_database(self, test_session: AsyncSession):
        """Test that deleted user (None) raises 401."""
        # This is similar to user not found but tests the scenario where
        # user was deleted between token issue and validation
        user_id = "deleted-user"
        payload = {
            "sub": user_id,
            "email": "deleted@example.com",
            "iss": ISSUER,
            "aud": AUDIENCE,
        }

        mock_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-token")

        with patch("src.auth.get_public_key", new_callable=AsyncMock) as mock_get_key:
            mock_get_key.return_value = "mock-pem-key"

            with patch("jwt.decode") as mock_decode:
                mock_decode.return_value = payload

                with patch.object(test_session, "get", new_callable=AsyncMock) as mock_get:
                    mock_get.return_value = None  # User deleted

                    with pytest.raises(HTTPException) as exc_info:
                        await get_current_user(mock_creds, test_session)

                    assert exc_info.value.status_code == 401


class TestJWTValidationErrors:
    """Test suite for JWT validation error scenarios."""

    @pytest.mark.asyncio
    async def test_expired_jwt_token(self, test_session: AsyncSession):
        """Test that expired JWT token raises 401."""
        mock_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="expired-token")

        with patch("src.auth.get_public_key", new_callable=AsyncMock) as mock_get_key:
            mock_get_key.return_value = {"kty": "OKP", "crv": "Ed25519", "alg": "EdDSA"}

            with patch("jwt.PyJWK") as mock_pyjwk:
                mock_key_instance = MagicMock()
                mock_key_instance.key = "mock-key"
                mock_pyjwk.return_value = mock_key_instance

                with patch("jwt.decode") as mock_decode:
                    mock_decode.side_effect = jwt.ExpiredSignatureError("Token expired")

                    with pytest.raises(HTTPException) as exc_info:
                        await get_current_user(mock_creds, test_session)

                    assert exc_info.value.status_code == 401
                    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    @pytest.mark.asyncio
    async def test_invalid_signature_jwt_token(self, test_session: AsyncSession):
        """Test that JWT with invalid signature raises 401."""
        mock_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="tampered-token")

        with patch("src.auth.get_public_key", new_callable=AsyncMock) as mock_get_key:
            mock_get_key.return_value = "mock-key"

            with patch("jwt.decode") as mock_decode:
                mock_decode.side_effect = jwt.InvalidSignatureError("Invalid signature")

                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(mock_creds, test_session)

                assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_wrong_issuer_jwt_token(self, test_session: AsyncSession):
        """Test that JWT with wrong issuer raises 401."""
        mock_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="wrong-issuer-token")

        with patch("src.auth.get_public_key", new_callable=AsyncMock) as mock_get_key:
            mock_get_key.return_value = "mock-key"

            with patch("jwt.decode") as mock_decode:
                mock_decode.side_effect = jwt.InvalidIssuerError("Invalid issuer")

                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(mock_creds, test_session)

                assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_wrong_audience_jwt_token(self, test_session: AsyncSession):
        """Test that JWT with wrong audience raises 401."""
        mock_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="wrong-aud-token")

        with patch("src.auth.get_public_key", new_callable=AsyncMock) as mock_get_key:
            mock_get_key.return_value = "mock-key"

            with patch("jwt.decode") as mock_decode:
                mock_decode.side_effect = jwt.InvalidAudienceError("Invalid audience")

                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(mock_creds, test_session)

                assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_malformed_jwt_token(self, test_session: AsyncSession):
        """Test that malformed JWT token raises 401."""
        mock_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="not.a.valid.jwt")

        with patch("src.auth.get_public_key", new_callable=AsyncMock) as mock_get_key:
            mock_get_key.return_value = "mock-key"

            with patch("jwt.decode") as mock_decode:
                mock_decode.side_effect = jwt.DecodeError("Not enough segments")

                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(mock_creds, test_session)

                assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_token_format(self, test_session: AsyncSession):
        """Test that invalid token format raises 401."""
        mock_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid-format")

        with patch("src.auth.get_public_key", new_callable=AsyncMock) as mock_get_key:
            mock_get_key.return_value = "mock-key"

            with patch("jwt.decode") as mock_decode:
                mock_decode.side_effect = jwt.PyJWTError("Invalid token format")

                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(mock_creds, test_session)

                assert exc_info.value.status_code == 401
                assert "Could not validate credentials" in exc_info.value.detail


class TestAttackScenarios:
    """Test suite for security attack scenarios."""

    @pytest.mark.asyncio
    async def test_token_with_algorithm_none_attack(self, test_session: AsyncSession):
        """Test protection against 'alg: none' attack."""
        mock_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="alg-none-token")

        with patch("src.auth.get_public_key", new_callable=AsyncMock) as mock_get_key:
            mock_get_key.return_value = "mock-key"

            with patch("jwt.decode") as mock_decode:
                mock_decode.side_effect = jwt.InvalidAlgorithmError("Invalid algorithm")

                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(mock_creds, test_session)

                assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_token_replay_with_expired_timestamp(self, test_session: AsyncSession):
        """Test that replayed expired tokens are rejected."""
        mock_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="replayed-token")

        with patch("src.auth.get_public_key", new_callable=AsyncMock) as mock_get_key:
            mock_get_key.return_value = "mock-key"

            with patch("jwt.decode") as mock_decode:
                mock_decode.side_effect = jwt.ExpiredSignatureError("Token has expired")

                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(mock_creds, test_session)

                assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_token_with_tampered_payload(self, test_session: AsyncSession):
        """Test that tokens with tampered payload are rejected."""
        mock_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="tampered-payload")

        with patch("src.auth.get_public_key", new_callable=AsyncMock) as mock_get_key:
            mock_get_key.return_value = "mock-key"

            with patch("jwt.decode") as mock_decode:
                # Signature validation fails due to tampering
                mock_decode.side_effect = jwt.InvalidSignatureError("Signature verification failed")

                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(mock_creds, test_session)

                assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_pyjwk_conversion_error(self, test_session: AsyncSession):
        """Test error handling when PyJWK fails to convert JWK."""
        mock_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-token")

        with patch("src.auth.get_public_key", new_callable=AsyncMock) as mock_get_key:
            # Return a JWK dict to trigger PyJWK path
            mock_get_key.return_value = {"kty": "OKP", "crv": "Ed25519"}

            with patch("jwt.PyJWK") as mock_pyjwk:
                # PyJWK initialization fails
                mock_pyjwk.side_effect = jwt.PyJWTError("Invalid JWK format")

                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(mock_creds, test_session)

                assert exc_info.value.status_code == 401
