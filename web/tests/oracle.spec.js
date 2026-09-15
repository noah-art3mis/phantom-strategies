import { test, expect } from "@playwright/test";
test("the oracle can be consulted and retried on desktop and mobile", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.addInitScript(() => {
    const originalFetch = window.fetch;
    let calls = 0;
    window.fetch = (url, options) => {
      if (url !== "/api/consult" || calls++ > 0)
        return originalFetch(url, options);
      window.consultRequest = JSON.parse(options.body);
      const body = new ReadableStream({
        start(controller) {
          window.streamController = controller;
        },
      });
      window.pushEvent = (event) =>
        window.streamController.enqueue(
          new TextEncoder().encode(JSON.stringify(event) + "\n"),
        );
      window.pushEvent({ type: "delta", text: "The familiar" });
      return Promise.resolve(new Response(body));
    };
  });
  await page.goto("/");
  await expect(page.locator("#spectral-scene canvas")).toBeAttached();
  await expect(page.locator("h1")).toHaveScreenshot("title.png", {
    animations: "disabled",
    stylePath: "tests/title-snapshot.css",
  });
  // A cached navigation suspends and restores this document without rerunning modules.
  await page.evaluate(() => {
    window.dispatchEvent(
      new PageTransitionEvent("pagehide", { persisted: true }),
    );
    window.dispatchEvent(
      new PageTransitionEvent("pageshow", { persisted: true }),
    );
  });
  await expect(page.locator("#spectral-scene canvas")).toBeAttached();
  await page.locator("#question").fill("What do I desire?");
  await page.locator(".voice").filter({ hasText: "Spectral" }).click();
  await expect(page.locator("#temperature")).toHaveCount(0);
  await page.locator("#question").focus();
  await page.locator("#question").press("Shift+Enter");
  await expect(page.locator("#question")).toHaveValue("What do I desire?\n");
  await expect(page.locator("#response")).toBeHidden();
  await page.locator("#question").press("Enter");
  await expect(page.locator("#answer")).toHaveText("The familiar");
  await expect(page.locator("#reference")).toBeEmpty();
  await expect(page.locator(".summon")).toBeDisabled();
  expect(await page.evaluate(() => window.consultRequest)).toEqual({
    question: "What do I desire?",
    strategy: "Spectral",
    temperature: 1,
  });
  await page.evaluate(() => {
    window.pushEvent({ type: "delta", text: " becomes strange." });
    window.pushEvent({
      type: "done",
      content: "The familiar becomes strange.",
      author: "Hegel",
      strategy: "Spectral",
      book: "An imagined book",
      sentence: 42,
    });
    window.streamController.close();
  });
  await expect(page.locator("#answer")).toHaveText(
    "The familiar becomes strange.",
  );
  await expect(page.locator("#attribution")).toContainText("Hegel");
  await expect(page.locator("#fiction-note")).toBeVisible();
  await page.screenshot({ path: "test-results/desktop.png", fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.route("**/api/consult", (route) =>
    route.fulfill({
      status: 429,
      json: { detail: "Too many requests. Try again in 60 seconds." },
    }),
  );
  await page.getByRole("button", { name: "O, Prophet..." }).click();
  await expect(page.getByRole("alert")).toHaveText(
    "Too many requests. Try again in 60 seconds.",
  );
  await expect(
    page.getByRole("button", { name: "O, Prophet..." }),
  ).toBeEnabled();
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.screenshot({ path: "test-results/mobile.png", fullPage: true });
  expect(errors).toEqual([]);
});
