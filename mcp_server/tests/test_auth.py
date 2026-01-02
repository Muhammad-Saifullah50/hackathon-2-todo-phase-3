"""Test script for MCP server authentication.

This script tests the authentication flow of the MCP server to verify that:
1. JWT tokens are properly validated
2. Users are correctly authenticated from the backend database
3. Public keys are fetched from the jwks table
4. Tools reject unauthorized requests
5. Tools accept valid authorization tokens
"""

import asyncio
import asyncpg
import jwt
import json
from datetime import datetime, timezone, timedelta
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import base64

# Add parent directory to path to import auth and main modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set")

# Remove asyncpg scheme
DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
DATABASE_URL = DATABASE_URL.replace("+psycopg://", "postgresql://")

# JWT Configuration (matching Better Auth)
ALGORITHM = "EdDSA"
ISSUER = "todo-auth"
AUDIENCE = "todo-api"


async def setup_test_user_and_jwk(pool: asyncpg.Pool) -> tuple[str, str, ed25519.Ed25519PrivateKey]:
    """Set up a test user and JWT key in the database.

    Returns:
        tuple: (user_id, valid_token, private_key)
    """
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Check if test user exists
            user = await conn.fetchrow(
                'SELECT id, email FROM "user" WHERE email = $1',
                'mcp_test@example.com'
            )

            if user:
                user_id = user['id']
                print(f"✅ Found existing test user: {user['email']} (ID: {user_id})")
            else:
                # Create test user
                user_id = 'test-user-mcp-auth-12345'
                await conn.execute(
                    '''INSERT INTO "user" (id, email, name, created_at, updated_at)
                       VALUES ($1, $2, $3, $4, $4)
                       ON CONFLICT (id) DO NOTHING''',
                    user_id,
                    'mcp_test@example.com',
                    'MCP Test User',
                    datetime.now(timezone.utc)
                )
                print(f"✅ Created test user: mcp_test@example.com (ID: {user_id})")

            # Generate Ed25519 key pair for JWT signing
            private_key = ed25519.Ed25519PrivateKey.generate()
            public_key = private_key.public_key()

            # Get raw bytes of the public key
            public_key_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )

            # Convert to base64url (URL-safe base64 without padding)
            x_param = base64.urlsafe_b64encode(public_key_bytes).rstrip(b'=').decode('utf-8')

            # Create JWK (JSON Web Key) format
            jwk = {
                "kty": "OKP",  # Octet Key Pair
                "crv": "Ed25519",  # Curve
                "x": x_param,  # Public key
                "alg": "EdDSA"  # Algorithm
            }

            # Insert or update JWK in database
            await conn.execute(
                '''DELETE FROM jwks WHERE "publicKey" LIKE '%"kty":"OKP"%' '''
            )

            jwk_id = 'test-jwk-mcp-12345'
            await conn.execute(
                '''INSERT INTO jwks (id, "publicKey", "createdAt")
                   VALUES ($1, $2, $3)
                   ON CONFLICT (id) DO UPDATE SET "publicKey" = $2, "createdAt" = $3''',
                jwk_id,
                json.dumps(jwk),
                datetime.now(timezone.utc)
            )
            print(f"✅ Inserted JWK into database")

            # Create valid JWT token
            now = datetime.now(timezone.utc)
            expiration = now + timedelta(hours=1)

            payload = {
                "sub": user_id,
                "email": "mcp_test@example.com",
                "name": "MCP Test User",
                "email_verified": True,
                "iss": ISSUER,
                "aud": AUDIENCE,
                "iat": int(now.timestamp()),
                "exp": int(expiration.timestamp())
            }

            # Get private key in PEM format for PyJWT
            private_key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

            # Sign the token
            token = jwt.encode(payload, private_key_pem, algorithm=ALGORITHM)

            print(f"✅ Generated valid JWT token")

            return user_id, token, private_key


async def test_auth_module(pool: asyncpg.Pool, token: str, user_id: str):
    """Test the auth module directly."""
    print("\n" + "="*60)
    print("TEST 1: Testing auth module directly")
    print("="*60)

    from auth import verify_jwt_token, extract_user_id_from_authorization

    try:
        # Test 1: Verify JWT token
        print("\n📝 Test 1a: Verifying JWT token...")
        user_info = await verify_jwt_token(token, pool)
        print(f"✅ Token verified successfully!")
        print(f"   User ID: {user_info['user_id']}")
        print(f"   Email: {user_info['email']}")
        print(f"   Name: {user_info['name']}")
        assert user_info['user_id'] == user_id, "User ID mismatch"

        # Test 2: Extract user ID from Authorization header
        print("\n📝 Test 1b: Extracting user ID from Authorization header...")
        auth_header = f"Bearer {token}"
        extracted_user_id = await extract_user_id_from_authorization(auth_header, pool)
        print(f"✅ User ID extracted: {extracted_user_id}")
        assert extracted_user_id == user_id, "Extracted user ID mismatch"

        # Test 3: Invalid token format
        print("\n📝 Test 1c: Testing invalid token format...")
        try:
            await extract_user_id_from_authorization("InvalidFormat", pool)
            print("❌ Should have raised ValueError for invalid format")
        except ValueError as e:
            print(f"✅ Correctly rejected invalid format: {str(e)}")

        # Test 4: Missing authorization
        print("\n📝 Test 1d: Testing missing authorization...")
        try:
            await extract_user_id_from_authorization(None, pool)
            print("❌ Should have raised ValueError for missing auth")
        except ValueError as e:
            print(f"✅ Correctly rejected missing auth: {str(e)}")

        # Test 5: Invalid token
        print("\n📝 Test 1e: Testing invalid token...")
        try:
            invalid_auth = "Bearer invalid.token.here"
            await extract_user_id_from_authorization(invalid_auth, pool)
            print("❌ Should have raised ValueError for invalid token")
        except ValueError as e:
            print(f"✅ Correctly rejected invalid token: {str(e)}")

        print("\n✅ All auth module tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Auth module test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_mcp_tools(pool: asyncpg.Pool, token: str, user_id: str):
    """Test MCP tools with authentication."""
    print("\n" + "="*60)
    print("TEST 2: Testing MCP tools with authentication")
    print("="*60)

    # Import MCP tools
    from main import add_task, list_tasks, complete_task, update_task, delete_task

    auth_header = f"Bearer {token}"

    try:
        # Test 1: Add task with valid auth
        print("\n📝 Test 2a: Adding task with valid authentication...")
        result = await add_task(
            title="Test Task from MCP Auth",
            authorization=auth_header,
            description="Testing authentication",
            priority="high"
        )
        print(f"✅ Task added: {json.dumps(result, indent=2)}")
        assert result['success'] == True, "Task creation should succeed"
        task_id = result['task']['id']

        # Test 2: List tasks with valid auth
        print("\n📝 Test 2b: Listing tasks with valid authentication...")
        result = await list_tasks(authorization=auth_header)
        print(f"✅ Tasks listed: Found {result['count']} task(s)")
        assert result['success'] == True, "Task listing should succeed"
        assert result['count'] >= 1, "Should have at least one task"

        # Test 3: Update task with valid auth
        print("\n📝 Test 2c: Updating task with valid authentication...")
        result = await update_task(
            task_id=task_id,
            authorization=auth_header,
            title="Updated Test Task"
        )
        print(f"✅ Task updated: {result['message']}")
        assert result['success'] == True, "Task update should succeed"

        # Test 4: Complete task with valid auth
        print("\n📝 Test 2d: Completing task with valid authentication...")
        result = await complete_task(task_id=task_id, authorization=auth_header)
        print(f"✅ Task completed: {result['message']}")
        assert result['success'] == True, "Task completion should succeed"

        # Test 5: Delete task with valid auth
        print("\n📝 Test 2e: Deleting task with valid authentication...")
        result = await delete_task(task_id=task_id, authorization=auth_header)
        print(f"✅ Task deleted: {result['message']}")
        assert result['success'] == True, "Task deletion should succeed"

        # Test 6: Try to add task with invalid auth
        print("\n📝 Test 2f: Testing invalid authentication...")
        result = await add_task(
            title="Should Fail",
            authorization="Bearer invalid.token.here",
            description="This should fail"
        )
        print(f"✅ Invalid auth correctly rejected: {result['error']}")
        assert result['success'] == False, "Invalid auth should be rejected"

        # Test 7: Try to add task with missing auth
        print("\n📝 Test 2g: Testing missing authentication...")
        result = await add_task(
            title="Should Fail",
            authorization="",
            description="This should fail"
        )
        print(f"✅ Missing auth correctly rejected: {result['error']}")
        assert result['success'] == False, "Missing auth should be rejected"

        print("\n✅ All MCP tool tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ MCP tool test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def cleanup_test_data(pool: asyncpg.Pool):
    """Clean up test data."""
    print("\n" + "="*60)
    print("CLEANUP: Removing test data")
    print("="*60)

    async with pool.acquire() as conn:
        async with conn.transaction():
            # Delete test tasks
            await conn.execute(
                'DELETE FROM tasks WHERE user_id = $1',
                'test-user-mcp-auth-12345'
            )
            print("✅ Deleted test tasks")

            # Note: Keeping test user and JWK for potential manual testing
            # Uncomment below to remove them:
            # await conn.execute('DELETE FROM "user" WHERE id = $1', 'test-user-mcp-auth-12345')
            # await conn.execute('DELETE FROM jwks WHERE id = $1', 'test-jwk-mcp-12345')
            # print("✅ Deleted test user and JWK")


async def main():
    """Main test runner."""
    print("\n" + "="*60)
    print("MCP SERVER AUTHENTICATION TEST SUITE")
    print("="*60)
    print(f"\nDatabase: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'N/A'}")
    print(f"Issuer: {ISSUER}")
    print(f"Audience: {AUDIENCE}")
    print(f"Algorithm: {ALGORITHM}")

    # Create connection pool
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)

    try:
        # Setup test user and generate token
        user_id, token, private_key = await setup_test_user_and_jwk(pool)

        # Run tests
        test_results = []

        # Test 1: Auth module
        result1 = await test_auth_module(pool, token, user_id)
        test_results.append(("Auth Module", result1))

        # Test 2: MCP tools
        result2 = await test_mcp_tools(pool, token, user_id)
        test_results.append(("MCP Tools", result2))

        # Cleanup
        await cleanup_test_data(pool)

        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        all_passed = True
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
            if not result:
                all_passed = False

        print("\n" + "="*60)
        if all_passed:
            print("🎉 ALL TESTS PASSED! 🎉")
            print("="*60)
            print("\n✅ MCP server authentication is working correctly!")
            print("✅ Backend users can be authenticated via JWT tokens")
            print("✅ All MCP tools properly validate authentication")
        else:
            print("❌ SOME TESTS FAILED")
            print("="*60)
            print("\n⚠️  Please review the failures above")

    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
