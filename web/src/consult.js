const interrupted = () =>
  new Error("The connection to the oracle was interrupted. Please try again.");

export async function consult(request, onDelta, fetcher = fetch) {
  const response = await fetcher("/api/consult", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal: AbortSignal.timeout(180_000),
  });
  if (!response.ok) {
    let data;
    try {
      data = await response.json();
    } catch {
      throw interrupted();
    }
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Please check your question and try again.",
    );
  }
  if (!response.body) throw interrupted();
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  try {
    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value, { stream: !done });
      let boundary;
      while ((boundary = buffer.indexOf("\n")) !== -1) {
        const line = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 1);
        let event;
        try {
          event = JSON.parse(line);
        } catch {
          throw interrupted();
        }
        if (event?.type === "delta" && typeof event.text === "string") {
          onDelta(event.text);
        } else if (
          event?.type === "done" &&
          ["content", "author", "strategy", "book"].every(
            (key) => typeof event[key] === "string",
          ) &&
          Number.isInteger(event.sentence)
        ) {
          return event;
        } else if (
          event?.type === "error" &&
          typeof event.detail === "string"
        ) {
          throw new Error(event.detail);
        } else {
          throw interrupted();
        }
      }
      if (done) throw interrupted();
    }
  } finally {
    await reader.cancel().catch(() => {});
    reader.releaseLock();
  }
}
