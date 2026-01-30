#!/usr/bin/env python
"""
Verification script for API key permission system setup.

Run this to verify your configuration is correct before starting the API.
"""

import sys
from pathlib import Path


def check_env_file():
    """Check if .env file exists and has required variables."""
    print("✓ Checking .env file...")
    env_file = Path(".env")
    if not env_file.exists():
        print("  ❌ .env file not found!")
        print("  Create .env file with MONGO_URI and GCS_BUCKET_NAME")
        return False

    env_content = env_file.read_text()
    required_vars = ["MONGO_URI", "GCS_BUCKET_NAME"]
    missing = [var for var in required_vars if var not in env_content]

    if missing:
        print(f"  ❌ Missing required variables: {', '.join(missing)}")
        return False

    print("  ✅ .env file exists with required variables")
    return True


def check_api_keys_file():
    """Check if api_keys.yaml exists."""
    print("\n✓ Checking api_keys.yaml...")
    api_keys_file = Path("api_keys.yaml")
    if not api_keys_file.exists():
        print("  ❌ api_keys.yaml not found!")
        print("  Copy api_keys.yaml.example to api_keys.yaml")
        return False

    print("  ✅ api_keys.yaml exists")
    return True


def check_settings():
    """Check if settings can be loaded."""
    print("\n✓ Loading settings...")
    try:
        from peskas_api.core.config import get_settings
        settings = get_settings()
        print(f"  ✅ Settings loaded successfully")
        print(f"     MongoDB Database: {settings.mongodb_database}")
        print(f"     MongoDB Collection: {settings.mongodb_audit_collection}")
        print(f"     GCS Bucket: {settings.gcs_bucket_name}")
        print(f"     API Keys Config: {settings.api_keys_config_path}")
        return True
    except Exception as e:
        print(f"  ❌ Failed to load settings: {e}")
        return False


def check_api_keys():
    """Check if API keys can be loaded."""
    print("\n✓ Loading API keys...")
    try:
        from peskas_api.services.api_keys import get_api_key_service
        service = get_api_key_service()
        num_keys = len(service._registry.api_keys) if service._registry else 0
        print(f"  ✅ Loaded {num_keys} API keys")

        if num_keys > 0:
            print("\n  Available API keys:")
            for key_str, config in service._registry.api_keys.items():
                status = "✅ enabled" if config.enabled else "❌ disabled"
                key_preview = key_str[:20] + "..." if len(key_str) > 20 else key_str
                print(f"    - {config.name} ({key_preview}) - {status}")
                if config.permissions.allow_all:
                    print(f"      Permissions: Full access (allow_all)")
                else:
                    perms = []
                    if config.permissions.countries:
                        perms.append(f"countries={config.permissions.countries}")
                    if config.permissions.date_from or config.permissions.date_to:
                        perms.append(f"dates={config.permissions.date_from}..{config.permissions.date_to}")
                    if config.permissions.statuses:
                        perms.append(f"statuses={config.permissions.statuses}")
                    print(f"      Permissions: {', '.join(perms) if perms else 'None specified'}")

        return True
    except Exception as e:
        print(f"  ❌ Failed to load API keys: {e}")
        return False


def check_mongodb_connection():
    """Check MongoDB connection."""
    print("\n✓ Testing MongoDB connection...")
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from peskas_api.core.config import get_settings
        import asyncio

        settings = get_settings()

        async def test_connection():
            client = AsyncIOMotorClient(settings.mongodb_uri)
            try:
                # Test connection
                await client.admin.command('ping')
                print(f"  ✅ Successfully connected to MongoDB")

                # Check database and collection
                db = client[settings.mongodb_database]
                collection = db[settings.mongodb_audit_collection]

                # Try to count documents (will be 0 if collection is empty/new)
                count = await collection.count_documents({})
                print(f"     Database: {settings.mongodb_database}")
                print(f"     Collection: {settings.mongodb_audit_collection}")
                print(f"     Existing audit logs: {count}")
                return True
            except Exception as e:
                print(f"  ❌ MongoDB connection test failed: {e}")
                return False
            finally:
                client.close()

        return asyncio.run(test_connection())
    except Exception as e:
        print(f"  ❌ Failed to connect to MongoDB: {e}")
        print("     Check your MONGO_URI in .env file")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Peskas API - Permission System Verification")
    print("=" * 60)

    checks = [
        check_env_file,
        check_api_keys_file,
        check_settings,
        check_api_keys,
        check_mongodb_connection,
    ]

    results = [check() for check in checks]

    print("\n" + "=" * 60)
    if all(results):
        print("✅ All checks passed! Your setup is ready.")
        print("\nYou can now start the API:")
        print("  uvicorn peskas_api.main:app --reload")
        print("\nTest with an API key:")
        print("  curl -H 'X-API-Key: dev-admin-key-12345' \\")
        print("    'http://localhost:8000/api/v1/data/landings?country=zanzibar'")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
