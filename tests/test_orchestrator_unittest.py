import unittest

from artiisly_automation.connectors.mock_adapters import (
    MockArtislyDesignEngine,
    MockSalesChannelAdapter,
    MockSocialPublisher,
)
from artiisly_automation.core.models import (
    AutomationRequest,
    Channel,
    IntegrationConfig,
    ProductInput,
    SocialPlatform,
    SocialPostRequest,
    TaskState,
)
from artiisly_automation.core.repository import InMemoryTaskRepository
from artiisly_automation.core.service import AutomationOrchestrator


class OrchestratorTest(unittest.TestCase):
    def test_end_to_end_mock_automation(self) -> None:
        orchestrator = AutomationOrchestrator(
            design_engine=MockArtislyDesignEngine(),
            channel_adapters={
                Channel.pod: MockSalesChannelAdapter(Channel.pod),
                Channel.website: MockSalesChannelAdapter(Channel.website),
            },
            social_publishers={
                SocialPlatform.instagram: MockSocialPublisher(SocialPlatform.instagram),
            },
            repository=InMemoryTaskRepository(),
        )

        request = AutomationRequest(
            product=ProductInput(
                title="Geometric Fox Tee",
                niche="animals",
                style_prompt="Minimal geometric fox artwork with warm tones for a t-shirt front print.",
                target_channels=[Channel.pod, Channel.website],
                base_price=21.0,
            ),
            social=SocialPostRequest(platforms=[SocialPlatform.instagram], hashtags=["#fox"]),
            integrations=IntegrationConfig(),
        )

        result = orchestrator.run(request)
        self.assertEqual(result.state, TaskState.complete)
        self.assertEqual(len(result.result.channel_publications), 2)
        self.assertEqual(len(result.result.social_posts), 1)


if __name__ == "__main__":
    unittest.main()
