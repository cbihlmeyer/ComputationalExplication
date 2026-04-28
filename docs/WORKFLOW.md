#  Web Scrape and Preprocess Workflow

## Purpose
To better understand the wide-spread use of the term “grooming,” quantitative content analysis is used side-be-side qualitative methods, such as thematic analysis, elicitation (focus group, survey), and others. Web-scraping is used to gather targeted, unstructured text data on this term from TikTok.

---

## High-Level Steps
- Zeeschuimer Web Scrape
- Preprocess Metadata
- Extract URL
- Generate Whisper Transcripts
- Derive Supplemental Text Content Areas (Description, On-screen Text)
- Clean All Text Areas (Description, On-screen Text, Transcripts)
- Human Verification and Further Probing

---

## Step 1 — Zeeschuimer Web Scrape

**1a. Install extension**  
Download the Zeeschuimer extension for Firefox: https://github.com/digitalmethodsinitiative/zeeschuimer/releases
See the Zeeschuimer Worksheet for detailed instructions: https://docs.google.com/document/d/19MAiqX7Vx1FcNJ44K-vSdnKDVC5gcFwtrSQiewnwW8A/edit
Note: Zeeschuimer does not work in private browsing.


**1b. Design a search query**  
Manually navigate to a relevant TikTok page; everything the user sees will be recoded as metadata.  
Log in and use TikTok’s search feature to search for **“grooming”** videos.  
You can also view the hashtag page without logging in

**1c. Turn on the extension**  
Toggle the Zeeschuimer extension **on**.

**1d. Refresh and collect**  
Refresh the page after toggling to clear any cached data.  
Scroll until you have captured the desired amount of data (e.g., ~50 TikTok videos).

**1e. Export**  
Download the collected data as an **.ndjson** file.

---

## Step 2 — Preprocess raw metadata (R)
[Preprocess_sans_trans.Rmd](https://github.com/cbihlmeyer/ComputationalExplication/blob/77153ceca37700ad93b3fd1830f2915b603f3b2b/r/Preprocess_sans_trans.Rmd)

**2a. Un-nest the raw TikTok metadata**  

**2b. From raw TikTok metadata, derive variables:**  
1)	IDs/handles (item_id, author_id, author_handle)
2)	Core text surface (desc_raw)
3)	Engagement (engage_likes, comments, plays, shares, saves) 
4)	Hashtags (hashtags_list_raw)
5)	Time source (createTime, untransformed)
6)	Ad flag (is_ad_platform)
7)	Duration (duration_s)
8)	Text language (text_lang)
9)	Audio flags/metrics (audio_original_flag, audio_loudness_LUFs)

**2c. Derive and clean text content areas:**  
1)	Hashtags — found in description
2)	Description — caption text to the post, which includes hashtags and mentions
3)	On screen text — creator-added “stickers” overlayed on the video

**2d. Derive and clean text content areas:**  
-	Remove literal //n token if present
-	Convert literal backslash n (\n) to a single space
-	Flatten strings that look like R’s c("…", "…") printout into plain text
-	Drop leading c( or c(" (with optional spaces)
-	Drop trailing )
-	Remove all double quotes (ASCII and curly)
-	Replace actual CR/LF newlines with a single space
-	Normalize apostrophes to plain ASCII to avoid CSV mojibake
-	Drop zero width characters (ZWSP, ZWJ, ZWNJ, BOM)
-	Replace raw URLs with placeholder <URL>
-	Trim and collapse whitespace
-	Unicode normalize (NFC); e.g., U+006E n followed by U+0303 ~ → ñ
- (Optional) Lowercase for regex/search (Unicode safe)
-	HTML unescape (convert entities like &amp; to &)
-	Isolate emojis from description
-	Remove mentions (@) from description

**Optional: 2e. Create inclusion indicators**  
It can take a considerable amount of computing power to transcribe your data. You may want to filter out data based on your most broad/conservative criteria at this  point.


---

## Step 3 — Extract URL
[URL Extract.Rmd](https://github.com/cbihlmeyer/ComputationalExplication/blob/022d01e4c14efb6dd20856f20ecba35eb07b1332/r/URL%20Extract.Rmd)

**3a. Create permalinks in R**  
Use the raw Zeeschuimer metadata to derive a permalink for each video.

**3b. Build a CSV with columns**  
1)	author_id — TikTok’s internal, stable account identifier
2)	author_uniqueid — author username/handle
3)	item_id — unique ID for each video
4)	permalink — canonical TikTok URL:
https://www.tiktok.com/@{handle}/video/{item_id}


---

## Step 4 — Generate Whisper Transcripts (Python)

[Transcripts.py](https://github.com/cbihlmeyer/ComputationalExplication/blob/5f0e6e2823304a215443e19902349d4ebdd0eacc/python/Transcripts.py)

**4a. Transcribe from URLs**  
Use the permalink values to generate transcripts with the Whisper model.

---

## Step 5 — Merge Transcripts with Processed Metadata

[Preprocess_trans_merge.Rmd](https://github.com/cbihlmeyer/ComputationalExplication/blob/584610009133b4f0d950b13ad1eaeb64d098f5be/r/Preproc_trans_merge.Rmd)

**5a. Merge transcripts and metadata**  
Use the inc_key values to rbind the genererated transcripts with the cleaned metadata

**5b. Clean transcript content**  
Using the same cleaning steps as above, clean the transcript text areas


---

## Step 6 — Human Verification and Further Probing

**6a. Purpose of the tool**  
This pipeline aggregates and surfaces unstructured text data from user‑generated content on the selected topic—quickly and at scale. Over 4,700 TikTok videos were scraped using the Zeeschuimer tool. After cleaning for duplicates and inclusion criteria, this was reduced to 2k videos.

**6b. Content analytic methods**  
Design and apply content analysis to the cleaned text to detect the presence and contours of the phenomenon.

**6c. Validity checks (qualitative support)**  
- **Face Validity** — interpretive coherence within the concept; are units of analysis representative?  
  - *Practical step:* intercoder reliability with at least two coders.  
- **Semantic Validity** — do selected words/phrases share substantive meaning and differ from other concepts?  
  - *Practical step:* inspect cohesion and distinctiveness of the “grooming” unit of analysis.  
- **Construct Validity** — does the text reflect the construct of interest?  
  - *Practical step:* triangulate with other studies and/or external sources (e.g., focus groups eliciting the “grooming” concept).
