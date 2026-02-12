from django.test import TestCase
from tenants.infrastructure.hub import InfrastructureHub

class SmokeTest(TestCase):
    def test_hub_loads(self):
        """Verify that the InfrastructureHub can be imported and accessed without error."""
        try:
            hub = InfrastructureHub
            self.assertIsNotNone(hub.database)
            self.assertIsNotNone(hub.email)
            self.assertIsNotNone(hub.storage)
            self.assertIsNotNone(hub.identity)
            self.assertIsNotNone(hub.intelligence)
            self.assertIsNotNone(hub.audit)
            self.assertIsNotNone(hub.search)
            self.assertIsNotNone(hub.cache)
            self.assertIsNotNone(hub.queue)
            self.assertIsNotNone(hub.control)
        except Exception as e:
            self.fail(f"InfrastructureHub failed to load: {e}")
