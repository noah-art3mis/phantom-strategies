import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "tests",
  reporter: "dot",
  use: {
    baseURL: "http://127.0.0.1:5189",
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
    command: "npm run dev -- --port 5189 --strictPort",
    url: "http://127.0.0.1:5189",
    reuseExistingServer: false,
  },
});
