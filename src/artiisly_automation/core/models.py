from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator


class Channel(str, Enum):
    pod = "pod"
    website = "website"
    marketplace = "marketplace"
    social_commerce = "social_commerce"
    woocommerce = "woocommerce"
    printify = "printify"


class SocialPlatform(str, Enum):
    instagram = "instagram"
    facebook = "facebook"
    pinterest = "pinterest"
    x = "x"
    tiktok = "tiktok"


class ProductInput(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    niche: str = Field(min_length=2, max_length=120)
    style_prompt: str = Field(min_length=10, max_length=1200)
    target_channels: list[Channel] = Field(min_length=1)
    base_price: float = Field(gt=0)
    destination_url: HttpUrl | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("target_channels")
    @classmethod
    def channels_unique(cls, value: list[Channel]) -> list[Channel]:
        if len(set(value)) != len(value):
            raise ValueError("target_channels must be unique")
        return value


class GeneratedProduct(BaseModel):
    product_id: str
    title: str
    design_url: str
    variants: list[str]
    base_price: float


class PublishResult(BaseModel):
    channel: Channel
    listing_id: str
    status: str
    listing_url: str


class SocialPostRequest(BaseModel):
    platforms: list[SocialPlatform] = Field(default_factory=list)
    caption_template: str = Field(
        default="{title} now live. Shop now: {listing_url}",
        min_length=10,
        max_length=500,
    )
    hashtags: list[str] = Field(default_factory=list, max_length=20)


class SocialPostResult(BaseModel):
    platform: SocialPlatform
    status: str
    post_id: str


class IntegrationConfig(BaseModel):
    woocommerce_base_url: HttpUrl | None = None
    woocommerce_consumer_key: str | None = None
    woocommerce_consumer_secret: str | None = None
    printify_api_token: str | None = None
    printify_shop_id: str | None = None


class RevenuePlan(BaseModel):
    upsell_enabled: bool = True
    bundle_enabled: bool = True
    ad_campaign_seed_keywords: list[str] = Field(default_factory=list)


class AutomationResult(BaseModel):
    workflow_id: str
    generated_product: GeneratedProduct
    channel_publications: list[PublishResult]
    social_posts: list[SocialPostResult] = Field(default_factory=list)
    revenue_plan: RevenuePlan


class AutomationRequest(BaseModel):
    product: ProductInput
    social: SocialPostRequest = Field(default_factory=SocialPostRequest)
    integrations: IntegrationConfig = Field(default_factory=IntegrationConfig)


class TaskState(str, Enum):
    queued = "queued"
    running = "running"
    complete = "complete"
    failed = "failed"


class TaskRecord(BaseModel):
    workflow_id: str
    state: TaskState
    result: AutomationResult | None = None
    error: str | None = None
