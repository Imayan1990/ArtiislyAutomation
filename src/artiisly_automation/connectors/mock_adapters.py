from __future__ import annotations

import re
import uuid

from artiisly_automation.connectors.base import DesignEngine, SalesChannelAdapter, SocialPublisher
from artiisly_automation.core.models import (
    Channel,
    GeneratedProduct,
    ProductInput,
    PublishResult,
    SocialPlatform,
    SocialPostResult,
)


class MockArtislyDesignEngine(DesignEngine):
    """Deterministic connector to simulate Artisly design generation."""

    def generate(self, payload: ProductInput) -> GeneratedProduct:
        slug = re.sub(r"[^a-z0-9]+", "-", payload.title.lower()).strip("-")
        product_id = f"prd_{uuid.uuid4().hex[:10]}"
        return GeneratedProduct(
            product_id=product_id,
            title=payload.title,
            design_url=f"https://cdn.artiisly.local/designs/{slug or 'untitled'}-{product_id}.png",
            variants=["S", "M", "L", "XL"],
            base_price=payload.base_price,
        )


class MockSalesChannelAdapter(SalesChannelAdapter):
    def __init__(self, channel: Channel) -> None:
        self.channel = channel

    def publish(self, product: GeneratedProduct, payload: ProductInput) -> PublishResult:
        listing_id = f"{self.channel.value[:3]}_{uuid.uuid4().hex[:8]}"
        base = payload.destination_url if payload.destination_url else "https://commerce.local"
        return PublishResult(
            channel=self.channel,
            listing_id=listing_id,
            status="published",
            listing_url=f"{base}/listings/{listing_id}",
        )


class MockSocialPublisher(SocialPublisher):
    def __init__(self, platform: SocialPlatform) -> None:
        self.platform = platform

    def post(self, caption: str, media_url: str) -> SocialPostResult:
        return SocialPostResult(
            platform=self.platform,
            status="scheduled",
            post_id=f"{self.platform.value[:3]}_{uuid.uuid4().hex[:8]}",
        )
