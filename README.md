# Artiisly Automation Platform

A secure, enterprise-style automation service for generating products via Artisly-like design flow and publishing them to POD, website, WooCommerce, Printify, marketplace, and social commerce channels.

## Major Features

- **Secure API-first orchestration** with API key auth and basic rate limiting.
- **Product generation pipeline** with validated input contracts.
- **Multi-channel publishing** abstraction (POD, website, WooCommerce, Printify, marketplace, social commerce).
- **Social media posting orchestration** with platform-specific queueing.
- **Monetization planning** output (bundles, upsells, ad keyword seed generation).
- **Extensible connector architecture** for real integrations.
- **Workflow state tracking** for reliability and auditing.

## Architecture

- `api/routes.py`: FastAPI endpoints and integration-aware orchestrator wiring.
- `core/service.py`: orchestration logic for generation, publication, and social posting.
- `core/models.py`: strict data contracts and validation.
- `connectors/base.py`: integration interfaces.
- `connectors/mock_adapters.py`: mock Artisly, channel adapters, and social publisher.
- `connectors/production_adapters.py`: hosted WooCommerce + Printify + social webhook clients.
- `security/guards.py`: API key + sliding-window rate limiting.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
export ARTIISLY_AUTOMATION_API_KEY='super-secret-key'
export ARTIISLY_AUTOMATION_DRY_RUN='true'
uvicorn artiisly_automation.main:app --reload
```

Open API docs at `http://127.0.0.1:8000/docs`.

## Example End-to-End Request (WooCommerce + Printify + Social)

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/automation/workflows" \
  -H "Content-Type: application/json" \
  -H "x-api-key: super-secret-key" \
  -d '{
    "product": {
      "title": "Minimalist Cat T-Shirt",
      "niche": "pet lovers",
      "style_prompt": "Flat vector cat illustration in black and gold with retro typography",
      "target_channels": ["woocommerce", "printify", "website"],
      "base_price": 24.99,
      "destination_url": "https://store.example.com"
    },
    "integrations": {
      "woocommerce_base_url": "https://yourstore.com",
      "woocommerce_consumer_key": "ck_xxx",
      "woocommerce_consumer_secret": "cs_xxx",
      "printify_api_token": "pt_xxx",
      "printify_shop_id": "123456"
    },
    "social": {
      "platforms": ["instagram", "facebook", "pinterest"],
      "hashtags": ["#cats", "#tshirt", "#pod"]
    }
  }'
```

## Does it connect to hosted WooCommerce + Printify and automate social posting?

**Yes**, the code now includes concrete connector classes for:
- **WooCommerce hosted stores** via `wp-json/wc/v3/products`.
- **Printify** via `v1/shops/{shop_id}/products.json`.
- **Social posting** through webhook-based scheduling adapters.

By default `ARTIISLY_AUTOMATION_DRY_RUN=true`, so connectors can be validated safely without posting live data. Set it to `false` for real external calls.

## Enterprise Hardening Checklist

1. Store all API credentials in a secret manager (Vault/AWS/GCP/Azure).
2. Add idempotency keys and dedupe table to prevent duplicate product creation.
3. Move workflow execution to queue workers for high-volume processing.
4. Add retries with backoff and per-provider circuit breakers.
5. Add audit logs and trace IDs for every external request.
6. Add platform-specific policy checks for content and trademark safety.
7. Add signed webhooks and outbound request allow-lists.

## Common Design/Coding Issues and Mitigations

- **Issue: Tight coupling to one sales platform**
  - **Fix**: Keep provider adapters behind interfaces + dependency injection.
- **Issue: Duplicate product listings from retries**
  - **Fix**: idempotency keys + dedupe table.
- **Issue: Weak prompt governance**
  - **Fix**: prompt templates + policy validator before generation.
- **Issue: Security drift**
  - **Fix**: periodic key rotation, SAST/DAST, dependency scanning.
- **Issue: Hard-to-debug failures**
  - **Fix**: workflow state model, step-level telemetry, correlation IDs.

## Next Enterprise Upgrades

- Add Postgres + migration tool.
- Add async queue workers.
- Add OpenTelemetry and SIEM integration.
- Add policy engine for compliance filters.
- Add production SDK clients for all target marketplaces.
