import { expect, test } from "@playwright/test";
import { DashboardPage } from "../pages/DashboardPage";
import { ShortenPage } from "../pages/ShortenPage";

const BACKEND_URL = process.env.E2E_BACKEND_URL ?? "http://localhost:8000";

function uniqueAlias(prefix: string): string {
  return `${prefix}${Date.now().toString(36).slice(-8)}`.slice(0, 16);
}

test.describe("URL shortener core flow", () => {
  test("shortens a URL, redirects, and reflects the click on the dashboard", async ({
    page,
    request,
  }) => {
    const shortenPage = new ShortenPage(page);
    const alias = uniqueAlias("e2e");
    const destination = "https://example.com/e2e-target";

    await shortenPage.goto();
    await shortenPage.shorten(destination, { alias });

    const shortUrl = await shortenPage.getResultShortUrl();
    expect(shortUrl).toContain(alias);

    // The SPA does not own /{short_code} — real short-link clicks must hit
    // the FastAPI backend directly, not the Vite dev server.
    const redirectResponse = await request.get(shortUrl, { maxRedirects: 0 });
    expect(redirectResponse.status()).toBe(302);
    expect(redirectResponse.headers()["location"]).toBe(destination);

    const dashboardPage = new DashboardPage(page);
    await dashboardPage.goto();
    await expect(dashboardPage.clickCountFor(alias)).toHaveText("1");

    await dashboardPage.viewAnalyticsFor(alias);
    await expect(dashboardPage.analyticsPanelFor(alias)).toContainText("Total clicks: 1");
  });

  test("shortening without a custom alias generates a random 7-character code", async ({
    page,
  }) => {
    const shortenPage = new ShortenPage(page);
    await shortenPage.goto();
    await shortenPage.shorten("https://example.com/random-alias-target");

    const shortUrl = await shortenPage.getResultShortUrl();
    const code = shortUrl.split("/").pop() ?? "";
    expect(code).toHaveLength(7);
  });

  test("an expired link returns 410 and is marked expired on the dashboard", async ({
    page,
    request,
  }) => {
    // The UI's datetime-local input only has minute precision, which makes a
    // few-seconds-from-now expiry unreliable to set through the form (it can
    // round down into the past before submission). Create the link directly
    // via the API with a precise sub-minute expiry, then use the UI only to
    // verify redirect + dashboard behavior.
    const alias = uniqueAlias("exp");
    const expiresAt = new Date(Date.now() + 2000).toISOString();

    const createResponse = await request.post(`${BACKEND_URL}/api/v1/links`, {
      data: {
        original_url: "https://example.com/expiring-target",
        custom_alias: alias,
        expires_at: expiresAt,
      },
    });
    expect(createResponse.status()).toBe(201);
    const { short_url: shortUrl } = await createResponse.json();

    await page.waitForTimeout(2500);

    const redirectResponse = await request.get(shortUrl, { maxRedirects: 0 });
    expect(redirectResponse.status()).toBe(410);

    const dashboardPage = new DashboardPage(page);
    await dashboardPage.goto();
    await expect(dashboardPage.rowFor(alias)).toContainText("Expired");
  });

  test("taking an already-used alias shows an inline error", async ({ page }) => {
    const shortenPage = new ShortenPage(page);
    const alias = uniqueAlias("dup");

    await shortenPage.goto();
    await shortenPage.shorten("https://example.com/first", { alias });
    await expect(shortenPage.resultLink).toBeVisible();

    await shortenPage.destinationInput.fill("https://example.com/second");
    await shortenPage.aliasInput.fill(alias);
    await shortenPage.submitButton.click();

    await expect(shortenPage.errorBanner).toContainText(/already taken/i);
  });
});
