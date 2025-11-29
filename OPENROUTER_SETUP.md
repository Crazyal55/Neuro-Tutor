# OpenRouter API Key Setup Guide

This guide will help you add your OpenRouter API key to enable real AI responses in Neuro Tutor.

## 🔑 Getting Your OpenRouter API Key

### Step 1: Sign Up for OpenRouter
1. Go to [OpenRouter.ai](https://openrouter.ai/)
2. Click "Sign Up" and create an account
3. Verify your email address
4. Complete any required identity verification

### Step 2: Generate API Key
1. Log in to your OpenRouter dashboard
2. Navigate to "API Keys" section
3. Click "Create New Key"
4. Give your key a descriptive name (e.g., "Neuro Tutor Dev")
5. Copy the generated API key
6. **Important**: Store this key securely - you won't see it again

## ⚙️ Adding API Key to Neuro Tutor

### Method 1: Direct File Edit (Recommended)

1. **Navigate to Backend Directory**
   ```bash
   cd "C:\Users\alexa\Downloads\Project Rough\backend"
   ```

2. **Edit Environment File**
   - Open `.env` file in a text editor
   - Replace the placeholder with your real API key:
   ```env
   # OpenRouter Configuration
   OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
   
   # Application Settings
   DEBUG=False
   ```

3. **Save the File**
   - Save the `.env` file
   - Ensure no trailing spaces or special characters

### Method 2: Command Line (Advanced)

1. **Set Environment Variable**
   ```bash
   # For current session only
   export OPENROUTER_API_KEY="sk-or-v1-your-actual-api-key-here"
   
   # For permanent (add to your shell profile)
   echo 'export OPENROUTER_API_KEY="sk-or-v1-your-actual-api-key-here"' >> ~/.bashrc
   ```

2. **Or use PowerShell (Windows)**
   ```powershell
   $env:OPENROUTER_API_KEY="sk-or-v1-your-actual-api-key-here"
   ```

## ✅ Testing Your API Key

### Method 1: Run Test Script
```bash
cd backend
python test_openrouter.py
```

**Expected Success Output:**
```
🧠 Testing OpenRouter API with model: qwen2.5:72b-instruct
✅ OpenRouter API connection successful!

📝 Sample response:
--------------------------------------------------
[AI response about photosynthesis using Socratic method]
--------------------------------------------------
```

### Method 2: Start Backend and Test via Frontend
1. Start the backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

2. Start the frontend (in another terminal):
   ```bash
   cd socratic-tutor-frontend
   npm run dev
   ```

3. Open http://localhost:5180/
4. Send a test message like "Help me understand photosynthesis"

## 🔧 API Key Format

OpenRouter API keys typically follow this format:
```
sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Key Requirements:**
- Must start with `sk-or-v1-`
- Typically 48+ characters long
- Contains letters, numbers, and hyphens only

## 🛡️ Security Best Practices

### ✅ Do:
- Store API keys in environment variables
- Use different keys for development/production
- Rotate keys periodically
- Monitor usage in OpenRouter dashboard

### ❌ Don't:
- Commit API keys to git repositories
- Share API keys in public code
- Store keys in plain text files
- Use the same key across multiple projects

## 🚀 Troubleshooting

### Common Issues & Solutions

**Issue: "❌ Please set OPENROUTER_API_KEY"**
- **Solution**: Check that your `.env` file is in the correct directory
- **Solution**: Verify the key is properly formatted

**Issue: "❌ API Error: 401 Unauthorized"**
- **Solution**: Verify your API key is correct
- **Solution**: Check if the key has expired

**Issue: "❌ API Error: 429 Rate Limited"**
- **Solution**: Wait a few minutes before retrying
- **Solution**: Check your usage limits in OpenRouter dashboard

**Issue: "❌ API Error: 400 Bad Request"**
- **Solution**: Check model name spelling
- **Solution**: Verify request format

## 📊 Model Options

Neuro Tutor uses `qwen2.5:72b-instruct` by default, but you can change it:

**Popular Models:**
- `qwen2.5:72b-instruct` - Balanced performance
- `deepseek-chat` - Cost-effective option
- `meta-llama/llama-3.1-70b-instruct` - Advanced reasoning
- `anthropic/claude-3-haiku` - Fast responses

**To Change Model:**
1. Edit `backend/app/core/config.py`
2. Change `default_model` value
3. Restart backend server

## 🎯 Next Steps

Once your API key is working:

1. **Test Full Integration**
   - Send various questions to test Socratic method
   - Try different preference settings
   - Verify response quality

2. **Monitor Usage**
   - Check OpenRouter dashboard for API calls
   - Monitor costs and limits
   - Adjust model selection if needed

3. **Production Considerations**
   - Use production OpenRouter API keys
   - Set up monitoring and alerts
   - Consider rate limiting and caching

## 📞 Support

If you encounter issues:

- **OpenRouter Documentation**: https://openrouter.ai/docs
- **OpenRouter Status**: https://status.openrouter.ai/
- **Neuro Tutor Issues**: Check this project's troubleshooting section

---

*Last Updated: 2025-11-27*
*Status: Ready for Production*
