import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import HTTPException
from src.auth import get_current_user, ISSUER, AUDIENCE, TokenData
from src.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

@pytest.mark.asyncio
async def test_get_current_user_valid_token(test_session: AsyncSession):
    # Setup: Create a user in the test database
    user_id = "test-user-id"
    user = User(
        id=user_id,
        email="test@example.com",
        name="Test User",
    )
    test_session.add(user)
    await test_session.commit()

    # Mock token payload
    payload = {
        "sub": user_id,
        "email": "test@example.com",
        "iss": ISSUER,
        "aud": AUDIENCE,
    }

    # Mock the HTTPAuthorizationCredentials object
    class MockCreds:
        def __init__(self, token):
            self.credentials = token

    # Mock get_public_key, PyJWK, and jwt.decode
    with patch("src.auth.get_public_key", new_callable=AsyncMock) as mock_get_key:
        # Return a dict to trigger PyJWK path
        mock_get_key.return_value = {"kty": "OKP", "crv": "Ed25519", "x": "foo", "alg": "EdDSA"}
        
        with patch("jwt.PyJWK") as mock_pyjwk:
            mock_key_instance = MagicMock()
            mock_key_instance.key = "mock-key-object"
            mock_pyjwk.return_value = mock_key_instance
            
            with patch("jwt.decode") as mock_decode:
                mock_decode.return_value = payload
                
                # Execute
                result = await get_current_user(MockCreds("mock-token"), test_session)

                # Verify
                assert result.id == user_id
                assert result.email == "test@example.com"
                mock_decode.assert_called_once()
                mock_pyjwk.assert_called_once()

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(test_session: AsyncSession):
    # Mock the HTTPAuthorizationCredentials object
    class MockCreds:
        def __init__(self, token):
            self.credentials = token

    # Mock get_public_key, PyJWK and jwt.decode to raise an error
    with patch("src.auth.get_public_key", new_callable=AsyncMock) as mock_get_key:
        mock_get_key.return_value = {"kty": "OKP", "crv": "Ed25519", "x": "foo", "alg": "EdDSA"}
        
        with patch("jwt.PyJWK") as mock_pyjwk:
            mock_key_instance = MagicMock()
            mock_key_instance.key = "mock-key-object"
            mock_pyjwk.return_value = mock_key_instance
            
            with patch("jwt.decode") as mock_decode:
                mock_decode.side_effect = jwt.PyJWTError("Invalid token")
                
                # Execute & Verify
                with pytest.raises(HTTPException) as exc:
                    await get_current_user(MockCreds("invalid-token"), test_session)
                assert exc.value.status_code == 401
