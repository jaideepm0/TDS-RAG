**Important findins from the `data`**
- `topic_list` is the only useful key --> contains the `topics` and the `more_topics_url` (pointing to the next page to find topics)

**Important findings from the `data['topic_list']['topics']`**
- slug --> indicates the url directions as `/t/{slug}`
- id --> append the id `/t/{slug}/{id}`
- posts_count --> loop through the `/t/{slug}/{id}/{1..posts_count}`
- created at --> initial date of creation for the topic (between range)
- last_posted_at --> final post date in the topic (between range)

This should be good enough for us to scrape the posts content
---
 - convert the json to markdown based on content from each post (Images can be tricky)
 - orchestrate the code across range of dates
---
Finally if everything got right till now. Then we can safely embed and build the RAG

---


➜ jaideep@ArchLinux  ~/Programs/TDS/Project-1  uv run image.py
## Description for https://emoji.discourse-cdn.com/google/dog_face.png?v=14:
# Image Description

- **Subject**: A cartoon dog face
- **Features**:
  - The dog has a large, friendly expression.
  - It has a brown patch over one eye and a pink tongue sticking out.
  - The overall color scheme includes light brown, white, and shades of darker brown.
- **Style**: Simplified and playful, typical of emoji designs.
