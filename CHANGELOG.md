# Changelog

All notable changes to Ollama Gateway will be documented in this file.

## [1.0.0] - 2025-01-18

### Added

- Initial release of Ollama Gateway
- OpenAI-compatible API endpoint (`/v1/chat/completions`)
- Intelligent routing system based on prompt content analysis
- Support for local Ollama models (initially 9, currently 5):
  - qwen2.5-coder:7b (coding)
  - gemma2 (creative)
  - huihui_ai/qwen3-abliterated (multilingual)
  - llama3.2 (fast responses)
  - mistral (general/default)
- Health check endpoint (`/health`)
- Model listing endpoint (`/v1/models`)
- Gateway-specific routing test endpoint (`/gateway/route`)
- Streaming support for real-time responses
- Comprehensive logging system
- CORS support for web integrations
- Configuration via JSON file
- FastAPI-based architecture
- Integration guides for Claude-Code, Continue.dev, and Cursor
- Automated test suite
- Windows batch script for easy startup

### Features

- Automatic model selection based on:
  - Code-related keywords → deepseek-coder-v2
  - Chess-related keywords → deepseek-chess
  - Translation keywords → qwen2.5
  - Creative writing → gemma2
  - Speed requirements → llama3.2
  - General queries → mistral
- Priority-based model selection
- Tag-based matching system
- Fallback to default model when no match
- Long prompt detection (>4000 chars) routes to reasoning models

### Documentation

- Complete README with installation and usage
- Quick start guide (START-HERE.md)
- IDE integration guide (SETUP-CLAUDE-CODE.md)
- Comprehensive API documentation
- Troubleshooting section

### Developer Experience

- Python 3.9+ support
- Simple pip-based installation
- Hot-reload during development
- Clear error messages
- Structured logging
- Test automation script
