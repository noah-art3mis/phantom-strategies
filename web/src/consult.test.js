import test from "node:test";
import assert from "node:assert/strict";
import { consult } from "./consult.js";
const done = {
  type: "done",
  content: "An écho",
  author: "Hegel",
  strategy: "Spectral",
  book: "Imagined",
  sentence: 42,
};
const encode = (event) => JSON.stringify(event) + "\n";
test("delivers split Unicode tokens before the reference arrives", async () => {
  let controller;
  let first;
  const received = new Promise((resolve) => {
    first = resolve;
  });
  const body = new ReadableStream({
    start(value) {
      controller = value;
    },
  });
  const request = { question: "Why?", strategy: "Spectral", temperature: 1 };
  const tokens = [];
  let finished = false;
  const pending = consult(
    request,
    (text) => {
      tokens.push(text);
      first();
    },
    async (url, options) => {
      assert.equal(url, "/api/consult");
      assert.deepEqual(JSON.parse(options.body), request);
      return new Response(body);
    },
  ).then((result) => {
    finished = true;
    return result;
  });
  const bytes = new TextEncoder().encode(
    encode({ type: "delta", text: "An écho" }),
  );
  for (const byte of bytes) controller.enqueue(Uint8Array.of(byte));
  await received;
  assert.deepEqual(tokens, ["An écho"]);
  assert.equal(finished, false);
  controller.enqueue(new TextEncoder().encode(encode(done)));
  controller.close();
  assert.deepEqual(await pending, done);
});
test("reports HTTP limits and availability", async () => {
  for (const status of [429, 503]) {
    await assert.rejects(
      consult(
        {},
        () => {},
        async () =>
          Response.json({ detail: "Try again in 60 seconds." }, { status }),
      ),
      /60 seconds/,
    );
  }
});
test("retains delivered tokens and cancels the reader after a stream error", async () => {
  const tokens = [];
  let cancelled = false;
  const body = new ReadableStream({
    start(controller) {
      controller.enqueue(
        new TextEncoder().encode(
          encode({ type: "delta", text: "Partial" }) +
            encode({ type: "error", detail: "Please try again." }),
        ),
      );
    },
    cancel() {
      cancelled = true;
    },
  });
  await assert.rejects(
    consult(
      {},
      (text) => tokens.push(text),
      async () => new Response(body),
    ),
    /Please try again/,
  );
  assert.deepEqual(tokens, ["Partial"]);
  assert.equal(cancelled, true);
});
test("rejects truncated or malformed streams", async () => {
  for (const body of [
    encode({ type: "delta", text: "Partial" }),
    "not json\n",
    encode({ type: "done" }),
  ]) {
    await assert.rejects(
      consult(
        {},
        () => {},
        async () => new Response(body),
      ),
      /interrupted/i,
    );
  }
});
test("handles non-JSON proxy and structured validation errors", async () => {
  await assert.rejects(
    consult(
      {},
      () => {},
      async () => new Response("Bad Gateway", { status: 502 }),
    ),
    /interrupted/i,
  );
  await assert.rejects(
    consult(
      {},
      () => {},
      async () =>
        Response.json({ detail: [{ msg: "Invalid" }] }, { status: 422 }),
    ),
    /question/i,
  );
});
