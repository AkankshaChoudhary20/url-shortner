import type { Locator, Page } from "@playwright/test";

export class DashboardPage {
  readonly page: Page;
  readonly table: Locator;

  constructor(page: Page) {
    this.page = page;
    this.table = page.locator(".link-table");
  }

  async goto() {
    await this.page.goto("/");
    await this.page.getByRole("button", { name: "Dashboard" }).click();
  }

  rowFor(shortCode: string): Locator {
    return this.page.locator("tr", { has: this.page.getByRole("link", { name: new RegExp(shortCode) }) });
  }

  async viewAnalyticsFor(shortCode: string) {
    await this.rowFor(shortCode).getByRole("button", { name: /view analytics/i }).click();
  }

  analyticsPanelFor(shortCode: string): Locator {
    return this.rowFor(shortCode).locator("xpath=following-sibling::tr[1]").locator(".analytics-panel");
  }

  clickCountFor(shortCode: string): Locator {
    return this.rowFor(shortCode).locator("td").nth(2);
  }
}
