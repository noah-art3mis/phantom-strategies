# Streaming and request limits

## Request admission

`admission.py` is the source of truth for limits: per-visitor rolling minute and hour windows, a site-wide rolling minute window, and a simultaneous-request limit. Rejected requests return HTTP 429 with a `Retry-After` header and a readable retry message before invoking the oracle. Admitted attempts consume quota even if the provider fails. Health checks and static assets are outside these limits.

The deployment runs one Uvicorn worker. Quota history is bounded by the site-wide rate and expires after an hour. It lives in process memory and resets on restart, sleep/wake, or redeployment; multiple instances would each have their own allowance. This is abuse mitigation, not a persistent daily quota or a monetary spending cap. Configure an OpenAI project hard spend limit separately; a shared project limit can also affect the original Streamlit app.

On Render (`RENDER=true`), the app uses the rightmost address in `X-Forwarded-For`, treating the nearest proxy's appended address as authoritative and ignoring client-supplied prefixes. Uvicorn proxy-header rewriting is disabled in the Docker command so it cannot independently trust an attacker-controlled prefix. The public deployment must remain behind Render's ingress. Other hosting setups use the socket peer address and ignore forwarding headers. An extra proxy can group visitors under a shared address; verify forwarding behavior before changing the topology. Shared networks also share a per-IP allowance.

See [Render client IP and rate-limit guidance](https://render.com/articles/how-render-handles-ddos-attacks) and [OpenAI spend controls](https://developers.openai.com/api/docs/guides/spend-limits).

## Streaming contract

`POST /api/consult` keeps its JSON request body and returns `application/x-ndjson`: one JSON object per newline. `delta` events carry a `text` fragment; `done` carries the assembled `content`, `author`, `strategy`, `book`, and `sentence`. The frontend renders fragments as text, never HTML. The reference is generated only after the answer, with its own output-token cap in `genai.py`.

Failures before the first event use ordinary HTTP errors. Failures after streaming begins send an `error` event with a public `detail` string; an HTTP 200 alone therefore does not prove consultation completion. Only `done` marks success. A connection ending without it is incomplete. The browser preserves partial output and re-enables the form for retry.

Blocking provider work runs in worker threads, keeping the HTTP event loop available. The admission slot is held through the entire response, including reference generation. On disconnect, the response closes the oracle iterator, which closes the provider stream. An already-running synchronous provider read must return or reach its configured timeout before cleanup completes; the slot remains occupied during that interval. There are no automatic provider retries.

Responses disable caching and request proxy buffering be disabled. Browser tests exercise progressive rendering and rate-limit feedback; in-process HTTP tests establish token delivery before reference completion, concurrent-request rejection, and cleanup after disconnect. After deployment, verify one actual consultation visibly streams through Render's ingress. Existing browser tabs should be refreshed because the response contract changes with this release.
