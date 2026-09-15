import test from "node:test";
import assert from "node:assert/strict";
import { consult } from "./consult.js";

test("submits selected values and returns the answer", async () => {
  const request = { question: "Why?", strategy: "Spectral", temperature: 0.7 };
  const result = await consult(request, async (url, options) => {
    assert.equal(url, "/api/consult");
    assert.deepEqual(JSON.parse(options.body), request);
    return {
      ok: true,
      json: async () => ({ content: "An echo", author: "Hegel" }),
    };
  });
  assert.equal(result.content, "An echo");
});
test("reports server availability errors", async () => {
  await assert.rejects(
    consult({}, async () => ({
      ok: false,
      status: 503,
      json: async () => ({ detail: "The oracle is temporarily unavailable." }),
    })),
    /temporarily unavailable/,
  );
});
test("handles a non-JSON proxy failure", async () => {
  await assert.rejects(
    consult({}, async () => ({
      ok: false,
      status: 502,
      json: async () => {
        throw new SyntaxError();
      },
    })),
    /connection/i,
  );
});
test("does not show structured validation details as object Object", async () => {
  await assert.rejects(
    consult({}, async () => ({
      ok: false,
      status: 422,
      json: async () => ({ detail: [{ msg: "Invalid" }] }),
    })),
    /question/i,
  );
});
