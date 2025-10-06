# Security Best Practices

## API Key Management

### ✅ Current Security Setup

1. **Environment Variables**: All API keys are stored in `.env` file
2. **Git Protection**: `.env` is listed in `.gitignore` (never committed)
3. **Secure Loading**: Keys are loaded via `os.getenv()` at runtime
4. **Graceful Degradation**: System works without API keys (reduced functionality)

### 📋 Security Checklist

- [x] `.env` file is in `.gitignore`
- [x] API keys use environment variables
- [x] `.env.example` provided (without real keys)
- [x] No hardcoded secrets in code
- [ ] Rotate API keys periodically (recommended every 90 days)
- [ ] Use different keys for dev/staging/production

### 🔐 How to Store Your API Keys Securely

#### Option 1: Using .env File (Recommended for Development)

1. Create `.env` file in project root:
   ```bash
   cp .env.example .env
   ```

2. Add your API keys:
   ```bash
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_actual_key_here
   ```

3. Verify it's ignored by git:
   ```bash
   git status .env
   # Should show: nothing to commit (ignored)
   ```

#### Option 2: System Environment Variables (Recommended for Production)

Add to your shell profile (`~/.zshrc`, `~/.bashrc`, or `~/.bash_profile`):

```bash
export LLM_PROVIDER=gemini
export GEMINI_API_KEY=your_actual_key_here
```

Then reload:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

#### Option 3: Docker Secrets (Production)

For Docker deployments, use Docker secrets or environment files:

```yaml
# docker-compose.yml
services:
  api:
    environment:
      - LLM_PROVIDER=gemini
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    env_file:
      - .env
```

### ⚠️ What NOT to Do

❌ **Never** commit API keys to git
❌ **Never** hardcode API keys in source code
❌ **Never** share API keys in chat/email/slack
❌ **Never** expose API keys in client-side code
❌ **Never** log API keys in application logs

### 🔄 Key Rotation

If an API key is exposed:

1. **Immediately revoke** the compromised key
2. **Generate a new key** from the provider
3. **Update** your `.env` file
4. **Restart** the application
5. **Review** git history for any accidental commits

#### How to Revoke and Regenerate Keys:

- **Gemini**: https://makersuite.google.com/app/apikey
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/settings/keys

### 🛡️ Additional Security Measures

1. **Rate Limiting**: Gemini free tier has rate limits (60 requests/minute)
2. **Monitoring**: Monitor API usage in provider dashboards
3. **Least Privilege**: Only grant necessary permissions
4. **Audit Logs**: Review API access logs periodically

### 📝 Current API Key Status

Your current setup:
- ✅ API key stored in `.env` file
- ✅ File is git-ignored
- ✅ System configured to use Gemini

**IMPORTANT**: Since you shared the API key in this conversation, I recommend:
1. Go to https://makersuite.google.com/app/apikey
2. Delete the current key: `AIzaSyA2XBFcxw4gojoMBHVbp0xLlAqhAxOZPo8`
3. Create a new key
4. Update your `.env` file with the new key
5. Restart the backend server

### 🔍 Verifying Security

Check that your keys are not exposed:

```bash
# Make sure .env is ignored
git check-ignore .env
# Output: .env

# Search for any hardcoded keys (should return nothing)
git grep -i "AIzaSy"
git grep -i "sk-"
git grep -i "api_key"
```

### 🚀 Running the System Securely

```bash
# Load environment variables
source .env  # or let python-dotenv handle it

# Start the system
./start_system.sh
```

The system will automatically load keys from `.env` file using python-dotenv.
