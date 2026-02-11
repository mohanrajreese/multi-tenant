import threading

thread_local = threading.local()

def get_current_tenant():
    return getattr(thread_local, 'tenant', None)

def set_current_tenant(tenant):
    thread_local.tenant = tenant

def get_current_user():
    return getattr(thread_local, 'user', None)

def set_current_user(user):
    thread_local.user = user

def clear_context():
    """Clears the thread local context."""
    if hasattr(thread_local, 'tenant'):
        del thread_local.tenant
    if hasattr(thread_local, 'user'):
        del thread_local.user