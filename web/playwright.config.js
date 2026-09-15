import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "tests",
  reporter: "dot",
  use: {
    baseURL: "http://127.0.0.1:5177",
    launchOptions: {
      executablePath: "/usr/bin/google-chrome",
      args: [
        "--no-sandbox",
        "--use-gl=angle",
        "--use-angle=swiftshader",
        "--enable-unsafe-swiftshader",
      ],
    },
  },
  webServer: {
    command: "npm run dev",
    url: "http://127.0.0.1:5177",
    reuseExistingServer: true,
  },
});
