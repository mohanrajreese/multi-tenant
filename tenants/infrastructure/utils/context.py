import contextvars

# Context variables are natively async-safe and safer than threading.local()
# for modern coroutine-based worker environments.
_tenant_context = contextvars.ContextVar('tenant', default=None)
_user_context = contextvars.ContextVar('user', default=None)
_impersonator_context = contextvars.ContextVar('impersonator', default=None)

def get_current_tenant():
    """Returns the current tenant from the context."""
    return _tenant_context.get()

def set_current_tenant(tenant):
    """Sets the current tenant in the context."""
    _tenant_context.set(tenant)

def get_current_user():
    """Returns the current user from the context."""
    return _user_context.get()

def set_current_user(user):
    """Sets the current user in the context."""
    _user_context.set(user)

def get_current_impersonator():
    """Returns the current impersonator from the context."""
    return _impersonator_context.get()

def set_current_impersonator(user):
    """Sets the current impersonator in the context."""
    _impersonator_context.set(user)

def clear_context():
    """Resets the context variables to their default (None)."""
    _tenant_context.set(None)
    _user_context.set(None)
    _impersonator_context.set(None)