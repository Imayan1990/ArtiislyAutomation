from __future__ import annotations

import uuid

from artiisly_automation.connectors.base import DesignEngine, SalesChannelAdapter, SocialPublisher
from artiisly_automation.core.models import (
    AutomationRequest,
    AutomationResult,
    Channel,
    RevenuePlan,
    SocialPlatform,
    TaskRecord,
    TaskState,
)
from artiisly_automation.core.repository import InMemoryTaskRepository


class AutomationOrchestrator:
    def __init__(
        self,
        design_engine: DesignEngine,
        channel_adapters: dict[Channel, SalesChannelAdapter],
        social_publishers: dict[SocialPlatform, SocialPublisher],
        repository: InMemoryTaskRepository,
    ) -> None:
        self.design_engine = design_engine
        self.channel_adapters = channel_adapters
        self.social_publishers = social_publishers
        self.repository = repository

    def run(self, payload: AutomationRequest) -> TaskRecord:
        workflow_id = f"wrk_{uuid.uuid4().hex[:12]}"
        task = TaskRecord(workflow_id=workflow_id, state=TaskState.running)
        self.repository.save(task)

        try:
            generated_product = self.design_engine.generate(payload.product)
            publications = []
            for channel in payload.product.target_channels:
                adapter = self.channel_adapters.get(channel)
                if adapter is None:
                    raise ValueError(f"Unsupported channel requested: {channel.value}")
                publications.append(adapter.publish(generated_product, payload.product))

            primary_listing = publications[0].listing_url if publications else generated_product.design_url
            social_posts = []
            for platform in payload.social.platforms:
                publisher = self.social_publishers.get(platform)
                if publisher is None:
                    raise ValueError(f"Unsupported social platform requested: {platform.value}")

                caption = payload.social.caption_template.format(
                    title=generated_product.title,
                    listing_url=primary_listing,
                )
                if payload.social.hashtags:
                    caption = f"{caption} {' '.join(payload.social.hashtags)}"

                social_posts.append(publisher.post(caption=caption, media_url=generated_product.design_url))

            revenue_plan = RevenuePlan(
                ad_campaign_seed_keywords=[payload.product.niche, payload.product.title],
            )

            result = AutomationResult(
                workflow_id=workflow_id,
                generated_product=generated_product,
                channel_publications=publications,
                social_posts=social_posts,
                revenue_plan=revenue_plan,
            )
            task = TaskRecord(workflow_id=workflow_id, state=TaskState.complete, result=result)
            self.repository.save(task)
            return task
        except Exception as exc:  # fail-safe top-level guard for workflow state integrity
            task = TaskRecord(workflow_id=workflow_id, state=TaskState.failed, error=str(exc))
            self.repository.save(task)
            return task

    def get(self, workflow_id: str) -> TaskRecord | None:
        return self.repository.get(workflow_id)
