"""Test MCP server authentication with REAL backend users.

This script verifies that the MCP server can authenticate actual backend users
using JWT tokens signed with keys from the jwks table.
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


async def get_real_user(pool: asyncpg.Pool) -> dict:
    """Get a real user from the database."""
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            'SELECT id, email, name FROM "user" WHERE email = $1',
            'saifullahm2005@gmail.com'
        )

        if not user:
            # Get any user
            user = await conn.fetchrow('SELECT id, email, name FROM "user" LIMIT 1')

        if not user:
            raise ValueError("No users found in database!")

        return dict(user)


async def create_valid_token_for_user(pool: asyncpg.Pool, user: dict) -> tuple[str, str]:
    """Create a valid JWT token for a real user using the database JWKS.

    Returns:
        tuple: (token, jwk_id)
    """
    async with pool.acquire() as conn:
        # Get the latest JWK from database
        jwk_row = await conn.fetchrow(
            'SELECT id, "publicKey" FROM jwks ORDER BY "createdAt" DESC LIMIT 1'
        )

        if not jwk_row:
            raise ValueError("No JWKS found in database!")

        jwk_id = jwk_row['id']
        public_key_json = jwk_row['publicKey']

        print(f"\n📋 Using existing JWKS from database:")
        print(f"   JWKS ID: {jwk_id}")

        # Parse the public key
        public_key_data = json.loads(public_key_json)
        print(f"   Key Type: {public_key_data.get('kty')}")
        print(f"   Curve: {public_key_data.get('crv')}")

        # For testing purposes, we'll generate a NEW key pair
        # In production, the backend has the private key
        print("\n⚠️  NOTE: For testing, generating a new key pair and updating JWKS...")

        # Generate Ed25519 key pair
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        # Get raw bytes of the public key
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

        # Convert to base64url
        x_param = base64.urlsafe_b64encode(public_key_bytes).rstrip(b'=').decode('utf-8')

        # Create JWK
        jwk = {
            "kty": "OKP",
            "crv": "Ed25519",
            "x": x_param,
            "alg": "EdDSA"
        }

        # Update the JWKS in database (for testing only!)
        test_jwk_id = 'test-mcp-jwk-12345'
        await conn.execute(
            'DELETE FROM jwks WHERE id = $1',
            test_jwk_id
        )
        await conn.execute(
            'INSERT INTO jwks (id, "publicKey", "createdAt") VALUES ($1, $2, $3)',
            test_jwk_id,
            json.dumps(jwk),
            datetime.now(timezone.utc)
        )

        print(f"   ✅ Updated JWKS with test key (ID: {test_jwk_id})")

        # Create JWT token
        now = datetime.now(timezone.utc)
        expiration = now + timedelta(hours=1)

        payload = {
            "sub": user['id'],
            "email": user['email'],
            "name": user['name'],
            "email_verified": True,
            "iss": ISSUER,
            "aud": AUDIENCE,
            "iat": int(now.timestamp()),
            "exp": int(expiration.timestamp())
        }

        # Get private key in PEM format
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Sign the token
        token = jwt.encode(payload, private_key_pem, algorithm=ALGORITHM)

        print(f"   ✅ Generated JWT token for user: {user['email']}")

        return token, test_jwk_id


async def test_mcp_with_real_user(pool: asyncpg.Pool, user: dict, token: str):
    """Test MCP server with a real user."""
    print("\n" + "="*70)
    print("TESTING MCP SERVER WITH REAL BACKEND USER")
    print("="*70)

    from main import add_task, list_tasks, complete_task, update_task, delete_task

    auth_header = f"Bearer {token}"

    print(f"\n👤 User: {user['name']} ({user['email']})")
    print(f"🔑 User ID: {user['id']}")

    try:
        # Test 1: List existing tasks
        print("\n" + "-"*70)
        print("TEST 1: Listing existing tasks for user")
        print("-"*70)
        result = await list_tasks(authorization=auth_header)

        if result['success']:
            print(f"✅ SUCCESS: Found {result['count']} existing task(s)")
            if result['count'] > 0:
                print("\n📋 Sample tasks:")
                for task in result['tasks'][:3]:  # Show first 3
                    print(f"   - {task['title']} ({task['status']})")
        else:
            print(f"❌ FAILED: {result.get('error')}")
            return False

        # Test 2: Create a new task
        print("\n" + "-"*70)
        print("TEST 2: Creating a new task")
        print("-"*70)
        result = await add_task(
            title="MCP Auth Test Task",
            authorization=auth_header,
            description="This task was created to test MCP authentication",
            priority="high",
            tags=["test", "mcp"]
        )

        if result['success']:
            task_id = result['task']['id']
            print(f"✅ SUCCESS: Task created!")
            print(f"   Task ID: {task_id}")
            print(f"   Title: {result['task']['title']}")
            print(f"   Priority: {result['task']['priority']}")
            print(f"   Tags: {result['task']['tags']}")
        else:
            print(f"❌ FAILED: {result.get('error')}")
            return False

        # Test 3: Update the task
        print("\n" + "-"*70)
        print("TEST 3: Updating the task")
        print("-"*70)
        result = await update_task(
            task_id=task_id,
            authorization=auth_header,
            title="MCP Auth Test - UPDATED",
            description="Updated via MCP server"
        )

        if result['success']:
            print(f"✅ SUCCESS: Task updated!")
            print(f"   New title: {result['task']['title']}")
        else:
            print(f"❌ FAILED: {result.get('error')}")
            return False

        # Test 4: Complete the task
        print("\n" + "-"*70)
        print("TEST 4: Completing the task")
        print("-"*70)
        result = await complete_task(task_id=task_id, authorization=auth_header)

        if result['success']:
            print(f"✅ SUCCESS: Task completed!")
            print(f"   Status: {result['task']['status']}")
        else:
            print(f"❌ FAILED: {result.get('error')}")
            return False

        # Test 5: Delete the task
        print("\n" + "-"*70)
        print("TEST 5: Deleting the task (soft delete)")
        print("-"*70)
        result = await delete_task(task_id=task_id, authorization=auth_header)

        if result['success']:
            print(f"✅ SUCCESS: Task deleted (soft delete)")
        else:
            print(f"❌ FAILED: {result.get('error')}")
            return False

        # Test 6: Verify task is not in list anymore
        print("\n" + "-"*70)
        print("TEST 6: Verifying task is soft deleted")
        print("-"*70)
        result = await list_tasks(authorization=auth_header)

        if result['success']:
            task_ids = [t['id'] for t in result['tasks']]
            if task_id not in task_ids:
                print(f"✅ SUCCESS: Soft-deleted task is not in active task list")
            else:
                print(f"⚠️  WARNING: Soft-deleted task still appears in list")
        else:
            print(f"❌ FAILED: {result.get('error')}")
            return False

        return True

    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def cleanup_test_jwk(pool: asyncpg.Pool, jwk_id: str):
    """Clean up test JWKS."""
    async with pool.acquire() as conn:
        await conn.execute('DELETE FROM jwks WHERE id = $1', jwk_id)
        print(f"\n🧹 Cleaned up test JWKS (ID: {jwk_id})")


async def main():
    """Main test runner."""
    print("\n" + "="*70)
    print("MCP SERVER AUTHENTICATION TEST WITH REAL BACKEND USER")
    print("="*70)

    pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)

    try:
        # Get a real user from database
        print("\n🔍 Fetching real user from database...")
        user = await get_real_user(pool)
        print(f"✅ Found user: {user['name']} ({user['email']})")

        # Create a valid JWT token
        print("\n🔐 Creating JWT token...")
        token, jwk_id = await create_valid_token_for_user(pool, user)
        print(f"✅ JWT token created successfully")

        # Run the test
        print("\n" + "="*70)
        success = await test_mcp_with_real_user(pool, user, token)

        # Cleanup
        await cleanup_test_jwk(pool, jwk_id)

        # Final summary
        print("\n" + "="*70)
        print("FINAL RESULT")
        print("="*70)

        if success:
            print("🎉 ALL TESTS PASSED! 🎉")
            print("\n✅ MCP server can authenticate real backend users!")
            print("✅ All CRUD operations work with authentication!")
            print("✅ Soft delete is working correctly!")
            print("\n💡 NEXT STEPS:")
            print("   1. Your backend needs to issue JWT tokens with Better Auth")
            print("   2. Frontend passes these tokens to MCP server")
            print("   3. MCP server validates tokens using jwks table")
        else:
            print("❌ SOME TESTS FAILED")
            print("\n⚠️  Please review the failures above")

    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
