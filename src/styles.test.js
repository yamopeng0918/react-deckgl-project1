import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

const css = fs.readFileSync(path.resolve("src/styles.css"), "utf8");

describe("responsive styles", () => {
  it("allows narrow viewports instead of forcing a desktop minimum width", () => {
    expect(css).not.toMatch(/body\s*\{[^}]*min-width:\s*980px/s);
  });

  it("defines tablet and mobile layouts for the data lab interface", () => {
    expect(css).toContain("@media (max-width: 1100px)");
    expect(css).toContain("@media (max-width: 640px)");
    expect(css).toMatch(/\.workspace\s*\{[^}]*grid-template-columns:\s*1fr/s);
    expect(css).toMatch(/\.filter-row\s*\{[^}]*grid-template-columns:\s*1fr/s);
  });

  it("lets header and filter rows size to their content to avoid overlap", () => {
    expect(css).not.toMatch(/\.data-lab-shell\s*\{[^}]*grid-template-rows:\s*58px\s+76px\s+1fr/s);
    expect(css).toMatch(/\.data-lab-shell\s*\{[^}]*grid-template-rows:\s*auto\s+auto\s+minmax\(0,\s*1fr\)/s);
    expect(css).toMatch(/\.app-header\s*\{[^}]*min-height:\s*58px/s);
    expect(css).toMatch(/\.filter-row\s*\{[^}]*align-items:\s*stretch/s);
  });

  it("keeps the event table scrolling inside its panel on desktop", () => {
    expect(css).toMatch(/\.app-shell\s*\{[^}]*height:\s*max\(720px,\s*100vh\)/s);
    expect(css).toMatch(/\.workspace\s*\{[^}]*overflow:\s*hidden/s);
    expect(css).toMatch(/\.table-panel\s*\{[^}]*overflow:\s*auto/s);
  });

  it("lets selected event details scroll inside the summary panel", () => {
    expect(css).toMatch(/\.detail-panel\s*\{[^}]*grid-template-rows:\s*46px\s+minmax\(0,\s*1fr\)/s);
    expect(css).toMatch(/\.detail-body\s*\{[^}]*min-height:\s*0/s);
    expect(css).toMatch(/\.detail-body\s*\{[^}]*overflow:\s*auto/s);
  });
});
