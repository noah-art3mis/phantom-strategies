import { test, expect } from "@playwright/test";
test("the oracle can be consulted and retried on desktop and mobile", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.route("**/api/consult", async (route) => {
    expect(route.request().postDataJSON()).toEqual({
      question: "What do I desire?",
      strategy: "Spectral",
      temperature: 0.7,
    });
    await route.fulfill({
      json: {
        content: "The familiar becomes strange.",
        author: "Hegel",
        strategy: "Spectral",
        book: "An imagined book",
        sentence: 42,
      },
    });
  });
  await page.goto("/");
  await page.locator("#question").fill("What do I desire?");
  await page.locator(".voice").filter({ hasText: "Spectral" }).click();
  await page.locator("#temperature").fill("0.7");
  await page.getByRole("button", { name: "O, Prophet..." }).click();
  await expect(page.locator("#answer")).toHaveText(
    "The familiar becomes strange.",
  );
  await expect(page.locator("#attribution")).toContainText("Hegel");
  await expect(page.locator("#fiction-note")).toBeVisible();
  await page.screenshot({ path: "test-results/desktop.png", fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.route("**/api/consult", (route) =>
    route.fulfill({
      status: 503,
      json: { detail: "The oracle is temporarily unavailable." },
    }),
  );
  await page.getByRole("button", { name: "O, Prophet..." }).click();
  await expect(page.getByRole("alert")).toHaveText(
    "The oracle is temporarily unavailable.",
  );
  await expect(
    page.getByRole("button", { name: "O, Prophet..." }),
  ).toBeEnabled();
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.screenshot({ path: "test-results/mobile.png", fullPage: true });
  expect(errors).toEqual([]);
});
