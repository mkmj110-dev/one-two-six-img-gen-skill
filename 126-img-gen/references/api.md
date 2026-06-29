# 126 API Image Reference

## Authentication

Use:

```text
Authorization: Bearer <api-key>
```

Default base URL:

```text
https://chx126.xyz/v1
```

## image2 synchronous text-to-image

Endpoint:

```text
POST /v1/images/generations
Content-Type: application/json
```

Core request fields:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `model` | string | yes | `image2` |
| `prompt` | string | yes | Text prompt |
| `n` | number | no | Usually `1` |
| `size` | string | no | Common values: `1024x1024`, `1024x1536`, `1536x1024` |
| `response_format` | string | no | `url` or `b64_json` |
| `quality` | string | no | Pass only if supported by the upstream route |
| `style` | string | no | Pass only if supported by the upstream route |

Example:

```json
{
  "model": "image2",
  "prompt": "生成一张电商主图，白色背景，主体是一只金属质感保温杯",
  "size": "1024x1024",
  "n": 1,
  "response_format": "url"
}
```

## image2 synchronous image edit

Endpoint:

```text
POST /v1/images/edits
Content-Type: multipart/form-data
```

Core request fields:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `image` | file or file[] | yes | Source image file |
| `mask` | file | no | Transparent area marks the region to redraw |
| `model` | string | yes | `image2` |
| `prompt` | string | yes | Edit instruction |
| `n` | number | no | Usually `1` |
| `size` | string | no | Common values: `1024x1024`, `1024x1536`, `1536x1024` |
| `response_format` | string | no | `url` or `b64_json` |

## gpt-image-2 asynchronous image task

Submit endpoint:

```text
POST /v1/videos
Content-Type: application/json
```

Query endpoint:

```text
GET /v1/videos/{task_id}
```

Despite the `/videos` path, this is the image task flow for `gpt-image-2`.

Request fields:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `model` | string | yes | `gpt-image-2`, `gpt-image-2-2K`, or `gpt-image-2-4K`; keep `K` uppercase |
| `prompt` | string | yes | Text prompt |
| `aspect_ratio` | string | no | `auto`, `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`, `5:4`, `4:5`, `21:9` |
| `images` | string[] | no | Reference image URLs or complete Data URL Base64 strings; up to 5 |

Task statuses:

| Status | Meaning |
| --- | --- |
| `queued` | Waiting |
| `in_progress` | Running |
| `completed` | Use `url` |
| `failed` | Read `error.message` |

Poll every 2-5 seconds. Download completed image URLs promptly because they may expire.
