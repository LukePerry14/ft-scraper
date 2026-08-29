// import { log } from 'node:console';
// import { build_articles_json, extract_content, login } from './scraper/utils.js';

// const args = process.argv.slice(2);

// if (args.length === 0) {
//   console.error("Error: Parameters required.");
//   process.exit(1);
// }

// const command = args[0];
// const options = {
//   "override": false
// }

// let articleArgs = args.slice(1);
// const articles = new Set(articleArgs.filter(arg => arg !== "--override"));

// if (articleArgs.includes("--override")) {
//   options["override"] = true;
// }

// switch (command) {
//   case "full-pipeline":
//     await build_articles_json(options["override"]);
//     await extract_content(articles);
//     break;

//   case "get-articles":
//     await build_articles_json(options["override"]);
//     break;

//   case "extract-content":
//     await extract_content(articles);
//     break;

//   case "login":
//     await login();
// }

