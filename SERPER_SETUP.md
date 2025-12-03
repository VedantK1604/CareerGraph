# Getting Your Serper API Key

PathForge AI uses Serper API for real-time web search to find current resources. Here's how to get started:

## Why Serper?

- **Free Credits**: $50 in free credits to start
- **Affordable**: Only $5 per 1,000 searches after free credits
- **Fast & Reliable**: Built specifically for AI applications
- **Google Results**: Powered by Google Search
- **No Rate Limits**: Generous rate limits vs free alternatives

## Step 1: Create Serper Account

1. Go to [https://serper.dev](https://serper.dev)
2. Click **"Sign Up"** or **"Get Started Free"**
3. Sign up with your email or Google account
4. Verify your email address

## Step 2: Get Your API Key

1. After logging in, you'll see your dashboard
2. Your API key is displayed on the home page
3. Click **"Copy"** to copy your API key
4. It looks like: `a1b2c3d4e5f6...`

> **Note**: Keep this key secure! Don't share it publicly.

## Step 3: Add to PathForge AI

1. Open your `.env` file:
   ```bash
   cd /home/vedant/Desktop/testing_gravity
   nano .env
   ```

2. Add your Serper API key:
   ```
   SERPER_API_KEY=your_actual_serper_api_key_here
   SEARCH_ENABLED=true
   ```

3. Save and close (Ctrl+O, Enter, Ctrl+X)

4. Restart the server:
   ```bash
   # If server is running, stop it (Ctrl+C) and restart:
   uvicorn careergraph.main:app --reload
   ```

## Cost Estimates

### Free Tier
- **$50 free credits** = ~10,000 searches
- At 5-10 searches per roadmap = **1,000-2,000 free roadmaps**
- More than enough for testing and development!

### After Free Credits
- **$5 per 1,000 searches**
- **~$0.025-$0.05 per roadmap** (5-10 searches each)
- Combined with OpenAI: ~$0.18-$0.21 per roadmap total

### Monthly Estimates
- **Light Use** (10 roadmaps/month): ~$0.50
- **Moderate Use** (100 roadmaps/month): ~$5.00
- **Heavy Use** (500 roadmaps/month): ~$25.00

Much cheaper than other search APIs like SerpAPI!

## What Gets Searched?

For each roadmap, PathForge searches for:

1. **YouTube Videos** (2-3 per topic)
   - Recent tutorials and courses
   - Beginner-friendly content
   - High-quality channels

2. **Online Courses** (2-3 per topic)
   - Coursera, edX, Udemy
   - Current and active courses
   - Verified platforms

3. **Documentation** (1-2 per topic)
   - Official documentation
   - Getting started guides
   - API references

**Total**: ~5-10 searches per roadmap

## Verify It's Working

After adding your API key:

1. Generate a roadmap (e.g., "Roadmap for AI Engineer")
2. Check that resources have:
   - Real URLs (not example.com)
   - Source indicators (YouTube, Coursera, etc.)
   - Current content (2025 dates when shown)
3. Click on resource links to verify they work

## Disable Search (Optional)

If you want to disable web search and use LLM-only mode:

```bash
# In .env file:
SEARCH_ENABLED=false
```

This falls back to the original behavior (pre-trained LLM knowledge).

## Troubleshooting

### "Search results are empty"
- Check API key is correct in `.env`
- Verify `SEARCH_ENABLED=true`
- Check Serper dashboard for remaining credits
- Look at terminal for error messages

### "SerpAPI error"
- Ensure `google-search-results` package is installed:
  ```bash
  pip install google-search-results
  ```
- Check internet connection
- Verify Serper service is operational

### "Resources still using example.com"
- Search is disabled (check `SEARCH_ENABLED`)
- API key not set correctly
- Server not restarted after adding key

### Check API Usage

1. Go to [Serper Dashboard](https://serper.dev/dashboard)
2. View **Usage** tab
3. Monitor searches and remaining credits
4. Set up billing alerts if needed

## Best Practices

1. **Monitor Usage**: Check dashboard weekly
2. **Set Budgets**: Configure spending limits
3. **Cache Results**: Consider caching for repeated queries (future feature)
4. **Rotate Keys**: Use different keys for dev/prod
5. **Secure Keys**: Never commit `.env` to git (already in `.gitignore`)

## Alternative: SerpAPI

If you prefer SerpAPI instead:

1. Sign up at [serpapi.com](https://serpapi.com)
2. Get your API key
3. Use same `.env` variable: `SERPER_API_KEY`
4. The code works with both!

**Note**: SerpAPI is more expensive ($50/month for 5K searches vs Serper's $5/1K searches)

## Need Help?

- Serper Documentation: [serper.dev/docs](https://serper.dev/docs)
- Serper Support: support@serper.dev
- PathForge Issues: Check terminal logs for error messages

---

**Ready to start?** Once configured, your roadmaps will include real, current resources from across the web! 🚀

Return to [README.md](file:///home/vedant/Desktop/testing_gravity/README.md) for more information.
