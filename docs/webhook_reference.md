# 📡 Webhook API Reference (черновик)

События:
- post_published {channel_id, post_id, message_id, tags}
- digest_ready {channel_id, kind, period_start, period_end, url}

Безопасность: подпись HMAC-SHA256 по секрету интеграции.
