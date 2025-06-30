# Import all functions from the auth.dependencies module for backward compatibility
from auth.dependencies import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    get_current_active_user,
    authenticate_user,
    require_roles,
    is_super_admin,
    require_super_admin,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    pwd_context,
    oauth2_scheme
)