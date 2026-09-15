export async function consult(request, fetcher = fetch) {
  const response = await fetcher("/api/consult", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal: AbortSignal.timeout(180_000),
  });
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error(
      "The connection to the oracle was interrupted. Please try again.",
    );
  }
  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Please check your question and try again.",
    );
  }
  return data;
}
