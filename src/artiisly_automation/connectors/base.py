from __future__ import annotations

from abc import ABC, abstractmethod

from artiisly_automation.core.models import (
    GeneratedProduct,
    ProductInput,
    PublishResult,
    SocialPlatform,
    SocialPostResult,
)


class DesignEngine(ABC):
    @abstractmethod
    def generate(self, payload: ProductInput) -> GeneratedProduct:
        raise NotImplementedError


class SalesChannelAdapter(ABC):
    @abstractmethod
    def publish(self, product: GeneratedProduct, payload: ProductInput) -> PublishResult:
        raise NotImplementedError


class SocialPublisher(ABC):
    platform: SocialPlatform

    @abstractmethod
    def post(self, caption: str, media_url: str) -> SocialPostResult:
        raise NotImplementedError
