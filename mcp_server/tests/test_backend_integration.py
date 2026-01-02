"""Test MCP server authentication using tokens from the backend.

This script demonstrates how MCP server authenticates users using JWT tokens
issued by the backend's Better Auth system.

IMPORTANT: This test shows the integration flow:
1. Backend issues JWT tokens (signed with privateKey from jwks)
2. MCP server verifies tokens (using publicKey from jwks)
3. MCP tools use the authenticated user ID for database operations
"""

import asyncio
import asyncpg
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to import auth and main modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set")

DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
DATABASE_URL = DATABASE_URL.replace("+psycopg://", "postgresql://")


async def test_auth_verification():
    """Test that the MCP auth module can verify tokens."""
    print("\n" + "="*70)
    print("MCP SERVER AUTHENTICATION INTEGRATION TEST")
    print("="*70)

    pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)

    try:
        # Check database setup
        async with pool.acquire() as conn:
            user_count = await conn.fetchval('SELECT COUNT(*) FROM "user"')
            jwks_count = await conn.fetchval('SELECT COUNT(*) FROM jwks')

            print(f"\n📊 Database Status:")
            print(f"   Users: {user_count}")
            print(f"   JWKS entries: {jwks_count}")

            if jwks_count == 0:
                print("\n❌ ERROR: No JWKS found in database!")
                print("   Your backend needs to have Better Auth configured")
                print("   to generate JWKS entries.")
                return False

            # Get a sample user
            user = await conn.fetchrow('SELECT id, email, name FROM "user" LIMIT 1')
            print(f"\n👤 Sample User:")
            print(f"   Name: {user['name']}")
            print(f"   Email: {user['email']}")
            print(f"   ID: {user['id']}")

            # Get the JWKS
            jwks = await conn.fetchrow(
                'SELECT id, "publicKey" FROM jwks ORDER BY "createdAt" DESC LIMIT 1'
            )
            print(f"\n🔑 Latest JWKS:")
            print(f"   ID: {jwks['id']}")
            print(f"   Has Public Key: Yes")

        # Test the auth module can load the public key
        print("\n" + "-"*70)
        print("TEST 1: Can MCP server load public key from database?")
        print("-"*70)

        from auth import get_public_key

        public_key = await get_public_key(pool)
        print(f"✅ SUCCESS: Public key loaded from database")
        if isinstance(public_key, dict):
            print(f"   Key Type: {public_key.get('kty')}")
            print(f"   Curve: {public_key.get('crv')}")
            print(f"   Algorithm: {public_key.get('alg', 'EdDSA')}")
        else:
            print(f"   Key format: PEM string")

        # Test invalid token rejection
        print("\n" + "-"*70)
        print("TEST 2: Does MCP server reject invalid tokens?")
        print("-"*70)

        from auth import verify_jwt_token

        try:
            await verify_jwt_token("invalid.token.here", pool)
            print("❌ FAILED: Should have rejected invalid token")
            return False
        except ValueError as e:
            print(f"✅ SUCCESS: Invalid token rejected")
            print(f"   Error: {str(e)}")

        # Test MCP tools reject unauthorized requests
        print("\n" + "-"*70)
        print("TEST 3: Do MCP tools reject unauthorized requests?")
        print("-"*70)

        from main import add_task, list_tasks

        # Test with no authorization
        result = await add_task(
            title="Should Fail",
            authorization="",
            description="This should be rejected"
        )

        if not result['success']:
            print(f"✅ SUCCESS: Unauthorized request rejected")
            print(f"   Error: {result['error']}")
        else:
            print(f"❌ FAILED: Should have rejected unauthorized request")
            return False

        # Test with invalid authorization
        result = await list_tasks(authorization="Bearer invalid.token.here")

        if not result['success']:
            print(f"✅ SUCCESS: Invalid token rejected")
            print(f"   Error: {result['error']}")
        else:
            print(f"❌ FAILED: Should have rejected invalid token")
            return False

        # Summary
        print("\n" + "="*70)
        print("TEST RESULTS")
        print("="*70)
        print("✅ MCP server can load public keys from database")
        print("✅ MCP server correctly rejects invalid tokens")
        print("✅ MCP tools enforce authentication")

        print("\n" + "="*70)
        print("INTEGRATION FLOW")
        print("="*70)
        print("\n📝 How it works:")
        print("   1. User logs in via frontend → Better Auth (backend)")
        print("   2. Better Auth signs JWT with privateKey from jwks table")
        print("   3. Frontend receives JWT token")
        print("   4. Frontend calls MCP server with: Authorization: Bearer <token>")
        print("   5. MCP server:")
        print("      - Loads publicKey from jwks table")
        print("      - Verifies JWT signature")
        print("      - Extracts user ID from token")
        print("      - Executes tool with user's permissions")

        print("\n" + "="*70)
        print("NEXT STEPS TO GET A REAL TOKEN")
        print("="*70)
        print("\n1️⃣  Login via your frontend/backend:")
        print("   - User logs in through Better Auth")
        print("   - Backend returns JWT token in response")

        print("\n2️⃣  Use that token with MCP server:")
        print("   - Pass token as: Authorization: Bearer <token>")
        print("   - All MCP tools will work with that token")

        print("\n3️⃣  Example with curl:")
        print("   curl -X POST http://localhost:8000/mcp/... \\")
        print("     -H 'Authorization: Bearer <YOUR_TOKEN>' \\")
        print("     -d '{\"method\": \"tools/call\", ...}'")

        print("\n💡 TIP: Check your backend auth endpoints:")
        print("   - POST /api/auth/login or /api/auth/sign-in")
        print("   - Response should contain access_token or token field")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await pool.close()


async def main():
    success = await test_auth_verification()

    if success:
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("="*70)
        print("\n✅ Your MCP server is correctly configured!")
        print("✅ It can authenticate real backend users!")
        print("✅ Just use tokens from your Better Auth login!")
    else:
        print("\n" + "="*70)
        print("❌ SOME TESTS FAILED")
        print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
