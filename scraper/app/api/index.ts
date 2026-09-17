import express, { type Express, type Request, type Response, type NextFunction } from 'express';
import { chromium, type Browser, type BrowserContext } from 'playwright';
import { config } from '../config.js';
import { valid_login_context, build_articles_json, extract_content } from '../scraper/utils.js';

const PORT = 3000;

async function main() {
  const app: Express = express();
  app.use(express.json());
  
  const browser: Browser = await chromium.launch({ headless: false });
  const context: BrowserContext = await browser.newContext({ storageState: config.storageStatePath });

  app.post('/articles', async (req: Request, res: Response) => {
    const articlesJSON = await build_articles_json(context, PORT);

    return res.status(200).json({
      pageHTML: articlesJSON.pageHTML,
      articles: articlesJSON.articles
    });
  });

  app.post('/articles/:contentPath', async (req: Request, res: Response) => {

    const contentPath = req.params.contentPath;

    if (!(typeof contentPath === "string")) {
      return res.status(400).send("Invalid Article format: Expected string.");
    }

    const FullArticlesJSON = await extract_content(context, contentPath);

    return res.status(200).json({
      articles: FullArticlesJSON
    });
  })

  app.get('/session-status', async (req: Request, res: Response) => {
    try {
      const isValid = await valid_login_context();
      res.status(200).json({
        "validContext": Boolean(isValid)
      })
    } catch (error) {
      res.status(500).json({
        "validContext": false,
        "Error": `Failed to verify context with: ${error}`
      })
    }
  })

  const errorHandler = (
    err: any,
    req: Request,
    res: Response,
    next: NextFunction
  ) => {
    console.error(err.stack);

    const statusCode = err.statusCode || 500;

    return res.status(statusCode).json({
      error: err.message || "Internal Server Error"
    })
  }

  app.use(errorHandler);

  const server = app.listen(PORT, () => {
    console.log("Server listening on port 3000");
  });

  // Close the shared browser/context cleanly on shutdown, rather than
  // leaving an orphaned, never-logged-out session behind.
  const shutdown = async () => {
    console.log("Shutting down, closing browser...");
    server.close();
    await context.close();
    await browser.close();
    process.exit(0);
  };

  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
}

main().catch((err) => {
  console.error("Fatal startup error:", err);
  process.exit(1);
});
