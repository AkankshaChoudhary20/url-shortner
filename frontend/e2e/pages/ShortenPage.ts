import { expect, type Locator, type Page } from "@playwright/test";

export class ShortenPage {
  readonly page: Page;
  readonly destinationInput: Locator;
  readonly aliasInput: Locator;
  readonly expiresInput: Locator;
  readonly submitButton: Locator;
  readonly resultLink: Locator;
  readonly errorBanner: Locator;

  constructor(page: Page) {
    this.page = page;
    this.destinationInput = page.getByLabel("Destination URL");
    this.aliasInput = page.getByLabel("Custom alias (optional)");
    this.expiresInput = page.getByLabel("Expires at (optional)");
    this.submitButton = page.getByRole("main").getByRole("button", { name: /shorten/i });
    this.resultLink = page.locator(".result a");
    this.errorBanner = page.getByRole("alert");
  }

  async goto() {
    // "Shorten" is the default tab on load, so no tab click is needed here
    // (and the nav tab / submit button share the same accessible name).
    await this.page.goto("/");
    await this.destinationInput.waitFor();
  }

  async shorten(originalUrl: string, options: { alias?: string; expiresAt?: string } = {}) {
    await this.destinationInput.fill(originalUrl);
    if (options.alias) {
      await this.aliasInput.fill(options.alias);
    }
    if (options.expiresAt) {
      await this.expiresInput.fill(options.expiresAt);
    }
    await this.submitButton.click();
  }

  async getResultShortUrl(): Promise<string> {
    await expect(this.resultLink).toBeVisible();
    const href = await this.resultLink.getAttribute("href");
    if (!href) {
      throw new Error("Shortened link result did not render an href");
    }
    return href;
  }
}
