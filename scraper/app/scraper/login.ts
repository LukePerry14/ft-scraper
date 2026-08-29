import { chromium, type BrowserContext } from 'playwright';
import readline from 'node:readline/promises';
import { config } from '../config.js';
import path from 'node:path';
import { mkdir, access, constants } from 'node:fs/promises';


async function login() {
  console.log("Starting Login...")

  // Open Browser
  const browser = await chromium.launch({headless: false});
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto(config.loginUrl);
  // Confirm Login
  const rl = readline.createInterface({input: process.stdin, output: process.stdout});
  await rl.question("Press Enter when login is complete...");

  await rl.close();
  // Save Session information
  await mkdir(path.dirname(config.storageStatePath), {recursive: true});

  await context.storageState({path: config.storageStatePath});
  console.log("Saved Session information...")

  // cleanup
  await context.close();
  await browser.close();
}

await login();