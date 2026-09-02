# /backend

performs backend orchestration logic using fastapi. Connects to /scraper and /llm

# /frontend

Basic react frontend

# /llm

contains all logic for LLM usage for article summarisation and other LLM based tasks.

# /scraper

Typescript based logic to scrape the articles from the FT. Isolating metadata, title, and body. Then reformating the article to keep style, but inject custom content.


# /storage

Storage sub-container, using mysql for general document storage, and potentially lightweight vectorDB for similar article storage.


# TODO

<!-- 1) Build Scraper using headless browser
- get playwright working
- connect necessary auth
- isolate metadata (incl. title) + content
- reformat html to remove unnecessary content (footers etc.) -->

<!-- 2) Get LLMs to summarise content
- test different models + benchmark
- generate template? -->
- set up inference pipeline

3) Connect Scraper and LLM with fastapi backend

4) Build basic frontend
- Login Screen with FT login (remember login)
- retrieve title information and display as list
- list items selectable to generate summaries
- connect to backend
- second list with generated summaries (single page app)
- summarised items clickable to open formatted .html file.

5) Organise with Docker and batch script to make opening of app automatic (first working version)

6) Connect all information to mySQL backend to store information

7) Connect to frontend with historical articles

8) Connect with lookup using SQL

9) Create vectorDB using article metadata

10) Add similarity search for articles.

make job queue event driven