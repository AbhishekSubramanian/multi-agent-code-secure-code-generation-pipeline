# Ollama Setup Guide

This guide will help you set up Ollama to run the multi-agent system locally with open-source models like Llama, CodeLlama, and DeepSeek-Coder.

## Why Use Ollama?

- **100% Free**: No API costs
- **Privacy**: Runs entirely on your machine
- **No Internet Required**: Works offline once models are downloaded
- **Fast**: Local execution with GPU support
- **Easy Setup**: Simple installation and model management

---

## Step 1: Install Ollama

### Windows

1. **Download Ollama:**
   - Go to: https://ollama.com/download
   - Click "Download for Windows"
   - Run the installer (`OllamaSetup.exe`)

2. **Verify Installation:**
   ```powershell
   ollama --version
   ```
   You should see the version number (e.g., `ollama version 0.x.x`)

3. **Check if Ollama is Running:**
   ```powershell
   ollama list
   ```
   This should show an empty list (no models installed yet)

### macOS

```bash
# Install via Homebrew
brew install ollama

# Or download from website
# https://ollama.com/download
```

### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

---

## Step 2: Download a Code Model

Ollama needs to download models before you can use them. For code generation, these are the best options:

### Recommended: DeepSeek-Coder (Best for Code)

```bash
ollama pull deepseek-coder:6.7b
```

**Size:** ~3.8GB
**RAM Required:** ~8GB
**Quality:** Excellent for code generation

### Alternative: CodeLlama (Meta's Code Model)

```bash
ollama pull codellama:7b
```

**Size:** ~3.8GB
**RAM Required:** ~8GB
**Quality:** Very good, optimized for code

### Alternative: Qwen2.5-Coder (Strong Code Model)

```bash
ollama pull qwen2.5-coder:7b
```

**Size:** ~4.7GB
**RAM Required:** ~8GB
**Quality:** Excellent, newer model

### For Less Powerful Machines:

```bash
# Smaller, faster models (use less RAM)
ollama pull deepseek-coder:1.3b   # ~800MB, needs ~2GB RAM
ollama pull codellama:3b           # ~2GB, needs ~4GB RAM
```

---

## Step 3: Test Ollama

Test that Ollama is working:

```bash
# Test with a simple prompt
ollama run deepseek-coder:6.7b "Write a Python function to add two numbers"
```

You should see the model generate code!

**To exit the interactive mode, type:** `/bye`

---

## Step 4: Configure Your Project

### 1. Update Your `.env` File

Open your `.env` file and configure it for Ollama:

```bash
# Choose Ollama as the provider
LLM_PROVIDER=ollama

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=deepseek-coder:6.7b

# You can comment out Claude settings (not needed for Ollama)
# ANTHROPIC_API_KEY=...
# CLAUDE_MODEL=...
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install the `openai` package (used to communicate with Ollama's API).

---

## Step 5: Run the Multi-Agent System

Now you're ready to use the system with Ollama!

```bash
python example.py
```

Choose option 2 or 3 to test.

---

## Troubleshooting

### Issue: "Connection refused" or "Cannot connect to Ollama"

**Solution:** Make sure Ollama is running:

```bash
# Windows: Ollama should auto-start. If not, run:
ollama serve

# Linux/Mac: Start the service
ollama serve
```

### Issue: Model is very slow

**Causes:**
- Your machine doesn't have enough RAM
- No GPU available (CPU-only inference is slower)

**Solutions:**
1. Use a smaller model:
   ```bash
   ollama pull deepseek-coder:1.3b
   ```
   Then update `.env`:
   ```
   OLLAMA_MODEL=deepseek-coder:1.3b
   ```

2. Close other applications to free up RAM

### Issue: "Model not found"

**Solution:** Make sure you've pulled the model first:

```bash
# List downloaded models
ollama list

# If your model isn't there, pull it
ollama pull deepseek-coder:6.7b
```

### Issue: Generated code quality is poor

**Solutions:**
1. Try a different/larger model:
   ```bash
   ollama pull deepseek-coder:33b  # Larger, better quality
   ```

2. Make sure you're using a code-specialized model (not a general chat model)

3. Check that the model name in `.env` matches exactly:
   ```bash
   # List installed models
   ollama list

   # Copy the exact name to .env
   OLLAMA_MODEL=deepseek-coder:6.7b
   ```

---

## Available Code Models

| Model | Size | RAM | Quality | Best For |
|-------|------|-----|---------|----------|
| `deepseek-coder:1.3b` | 800MB | 2GB | Good | Low-end machines |
| `deepseek-coder:6.7b` | 3.8GB | 8GB | Excellent | Most users |
| `deepseek-coder:33b` | 19GB | 32GB | Best | High-end machines |
| `codellama:7b` | 3.8GB | 8GB | Very Good | General code |
| `codellama:13b` | 7.3GB | 16GB | Excellent | Better quality |
| `codellama:34b` | 19GB | 32GB | Best | High-end machines |
| `qwen2.5-coder:7b` | 4.7GB | 8GB | Excellent | Modern alternative |

---

## Switching Between Claude and Ollama

You can easily switch between Claude and Ollama by changing one line in your `.env`:

**For Ollama (Local, Free):**
```bash
LLM_PROVIDER=ollama
```

**For Claude (Cloud, Paid):**
```bash
LLM_PROVIDER=claude
```

Both work with the same code!

---

## Performance Tips

1. **Use GPU if available:** Ollama automatically uses GPU (NVIDIA/AMD)
2. **Close other apps:** Free up RAM for the model
3. **Use appropriate model size:** Bigger isn't always better if you don't have enough RAM
4. **Keep models updated:**
   ```bash
   ollama pull deepseek-coder:6.7b  # Re-download to update
   ```

---

## Next Steps

Once Ollama is set up:

1. Run the test suite:
   ```bash
   python test_system.py
   ```

2. Try the examples:
   ```bash
   python example.py
   # Choose option 2 and enter: "Create a function to calculate fibonacci numbers"
   ```

3. Read the main README.md for more usage examples

---

## Resources

- **Ollama Website:** https://ollama.com
- **Model Library:** https://ollama.com/library
- **Ollama GitHub:** https://github.com/ollama/ollama
- **DeepSeek-Coder:** https://github.com/deepseek-ai/DeepSeek-Coder

---

## FAQ

**Q: Do I need an API key for Ollama?**
A: No! Ollama runs locally and doesn't require any API keys.

**Q: Can I use Ollama and Claude together?**
A: Yes! Just switch the `LLM_PROVIDER` in `.env` when needed.

**Q: How much does Ollama cost?**
A: It's completely free! No costs, no limits.

**Q: Which model should I start with?**
A: Start with `deepseek-coder:6.7b` - it's the best balance of quality and performance.

**Q: Can I use this offline?**
A: Yes! Once models are downloaded, Ollama works completely offline.
