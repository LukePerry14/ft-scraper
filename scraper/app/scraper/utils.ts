import { chromium, type BrowserContext } from 'playwright';
import readline from 'node:readline/promises';
import { config } from '../config.js';
import { writeFile } from 'node:fs/promises';
import path from 'node:path';
import { mkdir, access, constants } from 'node:fs/promises';
import fs from 'fs/promises';

interface Article {
    title: String;
    topics: String[];
    contentPath: String;
    author: String;
    publishDate: Date;
    articleContent?: Array<string>;
}

type ArticleStore = Record<string, Article>;

type MetaArticleStore = {
  pageHTML: string,
  articles: ArticleStore
}

function _get_filename_json() {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}_${month}_${day}.json`;
}

const sleep = (delay: number) => new Promise((resolve) => setTimeout(resolve, delay));

async function valid_login_context() {
  try {
    await access(config.storageStatePath, constants.R_OK | constants.W_OK);
    return true;
  } catch {
    return false;
  }
}

async function _load_json(filePath: string) {
    const data = await fs.readFile(filePath, 'utf-8');
    const dataJSON = JSON.parse(data);
    return dataJSON;
}

async function render_summary(context: BrowserContext, contentPath: string, summaryData: string) {
  // Navigates to correct page and swaps out content for summary content
}

async function build_articles_json(context: BrowserContext, port: number): Promise<MetaArticleStore> {

  // Check login context exists
  if (!await valid_login_context()) {
    const err: any = new Error("Session invalid — re-authenticate manually via login()");
    err.statusCode = 401;
    throw err;
  }

  // One page per call, from the shared, already-authenticated context —
  // no new browser/session created here.
  const page = await context.newPage();

  try {
    const response = await page.goto('https://www.ft.com/', {waitUntil: 'domcontentloaded'});

    // Ensure page has loaded
    await page.waitForFunction( () => {
      return document.title === "Home - Financial Times"
    },
      { timeout: 1000 }
    )

    // Extract article elements
    const articles = await page.locator('.headline').all();


    // Populate article store with article information
    let stories: ArticleStore = {};

    for (const element of articles) {
      // Extract story information
      const title = await element.innerText()?? "NotFound";
      const contentPath = await element.evaluate((el) => el.querySelector('a')?.getAttribute('href'))?? "/notFound";
      const topic = await element.evaluate((el) => {
        return el.closest('[data-trackable-context-list-type]')?.getAttribute('data-trackable-context-list-type') ?? "Front Page";
      });

      if (topic === "podcasts") continue;

      let story = stories[contentPath];

      if (story) {
        if (!story.topics.includes(topic)) {
          story.topics.push(topic)
        }
      } else {
        stories[contentPath] = {
          title: title,
          topics: [topic],
          contentPath: contentPath
        };
      }
    }

    // Redirect all urls to point to localhost
    await page.evaluate((port) => {
    document.querySelectorAll('a[href]').forEach((link) => {
      const href = link.getAttribute('href');
      if (!href) return;

      try {
        const url = new URL(href, window.location.href);

        if (url.origin === 'https://www.ft.com' || url.origin === 'https://ft.com') {
          link.setAttribute(
            'href',
            `http://localhost:${port}${url.pathname}${url.search}${url.hash}`
          );
        }
      } catch {
        // ignore invalid links
      }
    });
  }, port);

    let metaFile: MetaArticleStore = {
      "pageHTML": await page.content(),
      "articles": stories,
    }

    //Write articles to JSON
    try {
      const filePath = path.join(process.cwd(), config.tmpStorage, _get_filename_json());

      // Create directory for the file
      await mkdir(path.dirname(filePath), { recursive: true });

      await writeFile(filePath, JSON.stringify(metaFile, null, 2));

      console.log("Saved article data to ", filePath);
    } catch (error) {
      console.log("Failed to save article data", error);
    }

    return metaFile;
  } finally {
    // Always close the page, even on error — never the shared context/browser.
    await page.close();
  }
}

async function extract_content(context: BrowserContext, article: string): Promise<MetaArticleStore> {

    if (!await valid_login_context()) {
      const err: any = new Error("Session invalid — re-authenticate manually via login()");
      err.statusCode = 401;
      throw err;
    }

    let articleObj: Article;
    articleObj.contentPath = article;

    const page = await context.newPage();

    try {
        for (let backoff = 0; backoff < config.maxBackoff; backoff++) {
            
            let response = await page.goto(config.homeURL + article.contentPath);

            if (response?.ok()) {
                const body = await page.locator("#article-body").first();
                const paragraphs = await body.locator("p").allInnerTexts()

                article.articleContent = paragraphs;

                dataJSON.articles[article_key] = article;
                break;
            }

            else if (response?.status() === 429) {
                let backoffTime = Math.pow(2, backoff) * 1000;
                console.log(`Hit Cloudflare throttling, retrying after ${backoffTime/1000}s...`);
                await sleep(backoffTime-1000);
            }

            else {
                console.error(`Unknown Error: ${response?.status()}`);
            }
            await sleep(1000);
        }
    

      await writeFile(filePath, JSON.stringify(dataJSON, null, 2));

      console.log("Saved article data to ", filePath);

      return dataJSON;
    } finally {
      await page.close();
    }
}

export { valid_login_context, build_articles_json, extract_content }