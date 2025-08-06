# Snowflake Keypair Authentication Issue

## Problem Summary
Users cannot use Snowflake keypair authentication with ToolFront's `Database` class.

## Current Behavior
When attempting to use keypair authentication:
```python
data = Database(
    url="snowflake://user@account/database/schema",
    authenticator="SNOWFLAKE_JWT",
    private_key=pkb  # private key bytes
)
```

Results in: `snowflake.connector.errors.ProgrammingError: 261006: Password is empty`

## Root Cause
1. ToolFront uses `ibis.connect(url, **kwargs)` in `database.py` line 135
2. When Ibis receives a Snowflake URL, it parses it and extracts `password=None` from the URL
3. This `password=None` is passed to the Snowflake connector
4. The Snowflake connector validates the password before checking the authenticator
5. The keypair authentication parameters (`authenticator`, `private_key`) are effectively ignored

## Verified Workaround
Using `ibis.snowflake.connect()` directly with explicit parameters works:
```python
import ibis

conn = ibis.snowflake.connect(
    user="user",
    account="account", 
    database="database",
    authenticator="SNOWFLAKE_JWT",
    private_key=pkb
)
```

## Additional Issue to Investigate
After successful connection with the workaround, user reports a CREATE DATABASE permission error. The exact cause needs investigation:
- Could be from `list_databases()` calling `SHOW SCHEMAS` (line 157 in database.py)
- Could be from table discovery logic
- Needs further debugging to identify the exact SQL command triggering this

## Proposed Solution

### Option 1: Special handling for Snowflake keypair auth
Modify `Database.model_validator()` to detect Snowflake + keypair auth and use `ibis.snowflake.connect()` directly:

```python
@model_validator(mode="after")
def model_validator(self) -> "Database":
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", "Unable to create Ibis UDFs", UserWarning)
        
        # Special handling for Snowflake keypair auth
        if (self.database_type == "snowflake" and 
            "authenticator" in self._connection_kwargs and
            self._connection_kwargs["authenticator"] in ["SNOWFLAKE_JWT", "snowflake_jwt"]):
            
            # Parse URL to extract connection params
            from urllib.parse import urlparse
            parsed = urlparse(self.url)
            
            # Extract user@account format
            user = parsed.username
            account = parsed.hostname
            
            # Extract database/schema from path
            path_parts = parsed.path.strip('/').split('/')
            database = path_parts[0] if path_parts else None
            schema = path_parts[1] if len(path_parts) > 1 else None
            
            # Connect using explicit parameters
            import ibis
            connect_params = {
                "user": user,
                "account": account,
                "database": database,
                **self._connection_kwargs
            }
            if schema:
                connect_params["schema"] = schema
                
            self._connection = ibis.snowflake.connect(**connect_params)
        else:
            # Standard connection for other databases
            self._connection = ibis.connect(self.url, **self._connection_kwargs)
    
    # Rest of validation logic...
```

### Option 2: Update Ibis
File an issue with Ibis to handle keypair auth properly when parsing Snowflake URLs.

## Open Questions
1. What specific SQL command is triggering the CREATE DATABASE permission error?
2. Are there other authentication methods (OAuth, SSO) that have similar issues?
3. Should we support BigQuery service account JSON files similarly?

## Testing Requirements
1. Test Snowflake with password auth (should still work)
2. Test Snowflake with keypair auth (both encrypted and unencrypted keys)
3. Test Snowflake with keypair auth using file path vs raw bytes
4. Test other databases to ensure no regression
5. Investigate and resolve the CREATE DATABASE permission issue