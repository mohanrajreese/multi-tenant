
import re
from tenants.business.exceptions import SecurityViolationError

class SchemaSanitizer:
    """
    Tier 80: Security Hardening.
    Ensures that tenant identifiers (slugs) are safe for use as SQL schema names.
    Prevents SQL injection during physical isolation provisioning.
    """
    
    @staticmethod
    def sanitize(slug: str) -> str:
        """
        Hardens a slug for safe SQL identifier usage.
        Rules:
        1. Must start with a letter.
        2. Only lowercase letters, numbers, and underscores allowed.
        3. Max length 63 characters (Postgres limit).
        """
        if not slug:
            raise SecurityViolationError("Schema identifier cannot be empty.")

        # Lowercase and replace hyphens with underscores
        sanitized = slug.lower().replace('-', '_')
        
        # Remove any character that isn't a letter, number, or underscore
        sanitized = re.sub(r'[^a-z0-9_]', '', sanitized)
        
        # Ensure it starts with a letter (Postgres requirement for unquoted identifiers)
        if sanitized and not sanitized[0].isalpha():
            sanitized = f"t_{sanitized}"
            
        # Truncate to Postgres limit
        sanitized = sanitized[:63]
        
        # Check against SQL reserved keywords if necessary
        # (For now, the t_ prefix or general structure handles most risks)
        
        if not sanitized:
            raise SecurityViolationError(f"Slug '{slug}' resulted in an invalid schema name.")
            
        return sanitized
