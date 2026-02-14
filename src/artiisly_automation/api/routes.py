from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException, status

from artiisly_automation.connectors.mock_adapters import (
    MockArtislyDesignEngine,
    MockSalesChannelAdapter,
    MockSocialPublisher,
)
from artiisly_automation.connectors.production_adapters import (
    JsonHttpClient,
    PrintifyAdapter,
    SocialWebhookPublisher,
    WooCommerceAdapter,
)
from artiisly_automation.core.models import (
    AutomationRequest,
    Channel,
    SocialPlatform,
    TaskRecord,
)
from artiisly_automation.core.repository import InMemoryTaskRepository
from artiisly_automation.core.service import AutomationOrchestrator
from artiisly_automation.security.guards import verify_api_key

router = APIRouter(tags=["automation"])

repository = InMemoryTaskRepository()


def _build_orchestrator(payload: AutomationRequest) -> AutomationOrchestrator:
    channel_adapters = {
        Channel.pod: MockSalesChannelAdapter(Channel.pod),
        Channel.website: MockSalesChannelAdapter(Channel.website),
        Channel.marketplace: MockSalesChannelAdapter(Channel.marketplace),
        Channel.social_commerce: MockSalesChannelAdapter(Channel.social_commerce),
    }

    dry_run = os.getenv("ARTIISLY_AUTOMATION_DRY_RUN", "true").lower() != "false"
    client = JsonHttpClient(dry_run=dry_run)

    if (
        payload.integrations.woocommerce_base_url
        and payload.integrations.woocommerce_consumer_key
        and payload.integrations.woocommerce_consumer_secret
    ):
        channel_adapters[Channel.woocommerce] = WooCommerceAdapter(
            base_url=str(payload.integrations.woocommerce_base_url),
            consumer_key=payload.integrations.woocommerce_consumer_key,
            consumer_secret=payload.integrations.woocommerce_consumer_secret,
            client=client,
        )

    if payload.integrations.printify_api_token and payload.integrations.printify_shop_id:
        channel_adapters[Channel.printify] = PrintifyAdapter(
            shop_id=payload.integrations.printify_shop_id,
            api_token=payload.integrations.printify_api_token,
            client=client,
        )

    social_publishers = {platform: MockSocialPublisher(platform) for platform in SocialPlatform}
    social_webhook = os.getenv("ARTIISLY_SOCIAL_WEBHOOK_URL")
    if social_webhook:
        for platform in SocialPlatform:
            social_publishers[platform] = SocialWebhookPublisher(platform, social_webhook, client)

    return AutomationOrchestrator(
        design_engine=MockArtislyDesignEngine(),
        channel_adapters=channel_adapters,
        social_publishers=social_publishers,
        repository=repository,
    )


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/automation/workflows", response_model=TaskRecord)
def start_workflow(payload: AutomationRequest, _: str = Depends(verify_api_key)) -> TaskRecord:
    orchestrator = _build_orchestrator(payload)
    return orchestrator.run(payload)


@router.get("/automation/workflows/{workflow_id}", response_model=TaskRecord)
def get_workflow(workflow_id: str, _: str = Depends(verify_api_key)) -> TaskRecord:
    task = repository.get(workflow_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return task
