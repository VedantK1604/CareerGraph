# Getting Your OpenAI API Key

CareerGraph requires an OpenAI API key to function. Here's how to get one:

## Step 1: Create OpenAI Account

1. Go to [https://platform.openai.com/signup](https://platform.openai.com/signup)
2. Sign up with your email or Google/Microsoft account
3. Verify your email address

## Step 2: Add Payment Method

1. Navigate to [https://platform.openai.com/account/billing](https://platform.openai.com/account/billing)
2. Click "Add payment method"
3. Enter your credit/debit card details
4. Set up billing limits if desired (recommended: $10-20/month for testing)

> **Note**: OpenAI requires a payment method even though GPT-4 usage is pay-as-you-go.

## Step 3: Generate API Key

1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Give it a name (e.g., "CareerGraph")
4. Copy the key immediately - **you won't see it again!**
5. Save it somewhere secure

## Step 4: Configure CareerGraph

1. Open the `.env` file in your CareerGraph directory:
   ```bash
   cd /home/vedant/Desktop/testing_gravity
   nano .env
   ```

2. Paste your API key:
   ```
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
   OPENAI_MODEL=gpt-4-turbo-preview
   ```

3. Save and close (Ctrl+O, Enter, Ctrl+X)

## Estimated Costs

CareerGraph uses GPT-4 which has the following approximate costs:

| Operation | LLM Calls | Est. Tokens | Cost per Roadmap |
|-----------|-----------|-------------|------------------|
| Validation | 1 | ~500 | $0.01 |
| Research | 1 | ~2000 | $0.06 |
| Structure | 1 | ~3000 | $0.09 |
| **Total** | **3** | **~5500** | **~$0.16** |

**Monthly estimates**:
- **Light use** (10 roadmaps): ~$1.60
- **Moderate use** (50 roadmaps): ~$8.00
- **Heavy use** (200 roadmaps): ~$32.00

> **Tip**: You can use `gpt-3.5-turbo` instead of GPT-4 for ~90% cost savings, but with lower quality results.

## Using GPT-3.5 Instead (Cheaper)

Edit `.env`:
```bash
OPENAI_MODEL=gpt-3.5-turbo
```

Cost reduction:
- GPT-4 Turbo: ~$0.16 per roadmap
- GPT-3.5 Turbo: ~$0.01 per roadmap

Trade-offs:
- Less detailed roadmaps
- Fewer high-quality resources
- Simpler structure
- But 94% cheaper!

## Free Alternatives

OpenAI offers **$5 in free credits** for new accounts. This gives you:
- ~30 roadmaps with GPT-4
- ~500 roadmaps with GPT-3.5

After that, you'll need to add payment.

## Security Best Practices

1. **Never commit `.env` to git**
   - Already in `.gitignore`
   - Contains sensitive credentials

2. **Use environment-specific keys**
   - Dev key for testing
   - Prod key for production

3. **Set usage limits**
   - OpenAI dashboard → Billing → Usage limits
   - Prevents unexpected charges

4. **Rotate keys regularly**
   - Every 90 days recommended
   - Immediately if compromised

## Troubleshooting

### "Invalid API key"
- Check for typos
- Ensure key starts with `sk-`
- Verify key hasn't been revoked
- Create a new key if needed

### "Rate limit exceeded"
- Free tier has lower rate limits
- Add payment method to increase limits
- Wait and retry after a minute

### "Insufficient quota"
- Add credits to your account
- Check billing dashboard
- Verify payment method is valid

### "Model not available"
- Ensure you have GPT-4 access
- Some accounts need to request access
- Fall back to `gpt-3.5-turbo`

## Alternative: Use Local LLM (Advanced)

For privacy or cost concerns, you can modify the code to use:
- **Ollama** (local models)
- **LM Studio** (local models)
- **Claude API** (Anthropic)
- **Gemini API** (Google)

This requires code changes in `careergraph/agents/graph.py` to swap the LLM provider.

## Need Help?

- OpenAI Documentation: [https://platform.openai.com/docs](https://platform.openai.com/docs)
- OpenAI Support: [https://help.openai.com](https://help.openai.com)
- Pricing: [https://openai.com/pricing](https://openai.com/pricing)

---

**Ready to start?** Once you have your API key configured in `.env`, you're all set!

Return to [QUICKSTART.md](file:///home/vedant/Desktop/testing_gravity/QUICKSTART.md) to launch the application.
