from __future__ import annotations

import base64
import json
import uuid
import urllib.request
from dataclasses import dataclass

from artiisly_automation.connectors.base import SalesChannelAdapter, SocialPublisher
from artiisly_automation.core.models import (
    Channel,
    GeneratedProduct,
    ProductInput,
    PublishResult,
    SocialPlatform,
    SocialPostResult,
)


@dataclass
class JsonHttpClient:
    timeout_seconds: int = 20
    dry_run: bool = True

    def post(self, url: str, payload: dict, headers: dict[str, str]) -> dict:
        if self.dry_run:
            return {"id": f"dry_{uuid.uuid4().hex[:8]}", "permalink": f"{url}/dry-run"}

        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url=url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))


class WooCommerceAdapter(SalesChannelAdapter):
    def __init__(
        self,
        base_url: str,
        consumer_key: str,
        consumer_secret: str,
        client: JsonHttpClient,
    ) -> None:
        self.channel = Channel.woocommerce
        self.base_url = base_url.rstrip("/")
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.client = client

    def publish(self, product: GeneratedProduct, payload: ProductInput) -> PublishResult:
        token = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode("utf-8")).decode("utf-8")
        endpoint = f"{self.base_url}/wp-json/wc/v3/products"
        response = self.client.post(
            endpoint,
            payload={
                "name": product.title,
                "type": "simple",
                "regular_price": f"{product.base_price:.2f}",
                "description": payload.style_prompt,
                "images": [{"src": product.design_url}],
            },
            headers={
                "Authorization": f"Basic {token}",
                "Content-Type": "application/json",
            },
        )
        listing_id = str(response.get("id", f"woo_{uuid.uuid4().hex[:8]}"))
        listing_url = response.get("permalink", f"{self.base_url}/product/{listing_id}")
        return PublishResult(channel=self.channel, listing_id=listing_id, status="published", listing_url=listing_url)


class PrintifyAdapter(SalesChannelAdapter):
    def __init__(self, shop_id: str, api_token: str, client: JsonHttpClient) -> None:
        self.channel = Channel.printify
        self.shop_id = shop_id
        self.api_token = api_token
        self.client = client

    def publish(self, product: GeneratedProduct, payload: ProductInput) -> PublishResult:
        endpoint = f"https://api.printify.com/v1/shops/{self.shop_id}/products.json"
        response = self.client.post(
            endpoint,
            payload={
                "title": product.title,
                "description": payload.style_prompt,
                "variants": [{"title": variant, "price": int(product.base_price * 100)} for variant in product.variants],
                "print_areas": [{"placeholders": [{"images": [{"src": product.design_url}]}]}],
            },
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            },
        )
        listing_id = str(response.get("id", f"prn_{uuid.uuid4().hex[:8]}"))
        return PublishResult(
            channel=self.channel,
            listing_id=listing_id,
            status="published",
            listing_url=f"https://printify.com/app/store/products/{listing_id}",
        )


class SocialWebhookPublisher(SocialPublisher):
    def __init__(self, platform: SocialPlatform, webhook_url: str, client: JsonHttpClient) -> None:
        self.platform = platform
        self.webhook_url = webhook_url
        self.client = client

    def post(self, caption: str, media_url: str) -> SocialPostResult:
        response = self.client.post(
            self.webhook_url,
            payload={"platform": self.platform.value, "caption": caption, "media_url": media_url},
            headers={"Content-Type": "application/json"},
        )
        return SocialPostResult(
            platform=self.platform,
            status="scheduled",
            post_id=str(response.get("id", f"soc_{uuid.uuid4().hex[:8]}")),
        )
