from abc import ABC, abstractmethod

class SSOProvider(ABC):
    @abstractmethod
    def verify_token(self, token):
        """
        Verify the raw token from the client.
        Returns a standardized dict: {'email': ..., 'first_name': ..., 'last_name': ...}
        """
        pass

    @abstractmethod
    def get_auth_url(self, redirect_uri):
        """
        Return the URL to initiate the SSO flow.
        """
        pass
