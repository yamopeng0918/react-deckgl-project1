import { readFileSync } from "node:fs";
import { describe, expect, test } from "vitest";

const packageJson = JSON.parse(readFileSync("package.json", "utf8"));
const vercelConfig = JSON.parse(readFileSync("vercel.json", "utf8"));

describe("Vercel dependency installation", () => {
  test("keeps local video tooling out of the website dependency graph", () => {
    expect(packageJson.dependencies?.hyperframes).toBeUndefined();
    expect(packageJson.devDependencies?.hyperframes).toBeUndefined();
    expect(packageJson.optionalDependencies?.hyperframes).toBeUndefined();
    expect(vercelConfig.installCommand).toBe("npm ci");
  });

  test("runs local video tooling on demand at the documented version", () => {
    for (const scriptName of ["hf:doctor", "hf:preview", "hf:render"]) {
      expect(packageJson.scripts[scriptName]).toContain(
        "npx.cmd --yes hyperframes@0.7.45",
      );
    }
  });
});
