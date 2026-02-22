import { test, expect } from "@playwright/test";

const BASE_URL = "http://localhost:5173";
const API_URL = "http://localhost:8000/api/v1";

const testUser = {
  email: `e2e_${Date.now()}@test.com`,
  username: `e2euser_${Date.now()}`,
  password: "StrongPass123!",
};

test.describe("User Journey - Authentication", () => {
  test("shows login page at root", async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page.getByText("LevelUp Life")).toBeVisible();
    await expect(page.getByRole("button", { name: /login/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /register/i })).toBeVisible();
  });

  test("can switch between login and register mode", async ({ page }) => {
    await page.goto(BASE_URL);
    await page.getByRole("button", { name: /register/i }).click();
    await expect(page.getByPlaceholder("hero_name")).toBeVisible();
  });

  test("shows error on bad login credentials", async ({ page }) => {
    await page.goto(BASE_URL);
    await page.getByPlaceholder("your@email.com").fill("nobody@example.com");
    await page.getByPlaceholder("••••••••").fill("wrongpassword");
    await page.getByRole("button", { name: /enter the arena/i }).click();
    await expect(
      page.locator("p.text-red-400, [class*='text-red']")
    ).toBeVisible({ timeout: 5000 });
  });
});

test.describe("User Journey - Registration and Navigation", () => {
  test("can register a new account", async ({ page }) => {
    await page.goto(BASE_URL);
    await page.getByRole("button", { name: /register/i }).click();

    await page.getByPlaceholder("your@email.com").fill(testUser.email);
    await page.getByPlaceholder("hero_name").fill(testUser.username);
    await page.getByPlaceholder("••••••••").fill(testUser.password);
    await page.getByRole("button", { name: /begin your journey/i }).click();

    await expect(page).not.toHaveURL(BASE_URL, { timeout: 5000 });
  });

  test("redirects unauthenticated users to login", async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    await expect(page.getByText("LevelUp Life")).toBeVisible({ timeout: 5000 });
  });
});

test.describe("API Security - Ownership Enforcement", () => {
  test("cannot access protected endpoints without token", async ({ request }) => {
    const resp = await request.get(`${API_URL}/users/me`);
    expect([401, 403]).toContain(resp.status());
  });

  test("cannot access quests without token", async ({ request }) => {
    const resp = await request.get(`${API_URL}/quests/today`);
    expect([401, 403]).toContain(resp.status());
  });

  test("cannot complete another user's quest", async ({ request }) => {
    const userA = {
      email: `sec_a_${Date.now()}@test.com`,
      username: `sec_a_${Date.now()}`,
      password: "StrongPass123!",
    };
    const userB = {
      email: `sec_b_${Date.now()}@test.com`,
      username: `sec_b_${Date.now()}`,
      password: "StrongPass123!",
    };

    const regA = await request.post(`${API_URL}/auth/register`, { data: userA });
    const tokenA = (await regA.json()).access_token;

    const regB = await request.post(`${API_URL}/auth/register`, { data: userB });
    const tokenB = (await regB.json()).access_token;

    const questResp = await request.post(`${API_URL}/quests/`, {
      data: {
        title: "Security Test Quest",
        description: "Should not be completeable by others",
        domain: "fitness",
        difficulty: "easy",
        xp_reward: 50,
      },
      headers: { Authorization: `Bearer ${tokenA}` },
    });
    const quest = await questResp.json();

    const completeResp = await request.post(
      `${API_URL}/quests/${quest.id}/complete`,
      { headers: { Authorization: `Bearer ${tokenB}` } }
    );
    expect(completeResp.status()).toBe(404);
  });

  test("cannot delete another user's quest", async ({ request }) => {
    const userA = {
      email: `del_a_${Date.now()}@test.com`,
      username: `del_a_${Date.now()}`,
      password: "StrongPass123!",
    };
    const userB = {
      email: `del_b_${Date.now()}@test.com`,
      username: `del_b_${Date.now()}`,
      password: "StrongPass123!",
    };

    const regA = await request.post(`${API_URL}/auth/register`, { data: userA });
    const tokenA = (await regA.json()).access_token;

    const regB = await request.post(`${API_URL}/auth/register`, { data: userB });
    const tokenB = (await regB.json()).access_token;

    const questResp = await request.post(`${API_URL}/quests/`, {
      data: {
        title: "Quest to protect",
        description: "Should not be deleteable by others",
        domain: "learning",
        difficulty: "easy",
        xp_reward: 50,
      },
      headers: { Authorization: `Bearer ${tokenA}` },
    });
    const quest = await questResp.json();

    const deleteResp = await request.delete(`${API_URL}/quests/${quest.id}`, {
      headers: { Authorization: `Bearer ${tokenB}` },
    });
    expect(deleteResp.status()).toBe(404);
  });
});
