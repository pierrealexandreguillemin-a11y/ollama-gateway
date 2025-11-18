# Contributing to Ollama Gateway

Thank you for your interest in contributing to Ollama Gateway!

## Getting Started

### Prerequisites
- Python 3.9 or higher
- Ollama installed and running locally
- At least one Ollama model installed

### Setup Development Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd ollama-gateway

# Install dependencies
pip install -r requirements.txt

# Run the gateway
python main.py
```

## Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings to all functions and classes
- Keep functions focused and small

### Testing
Before submitting a PR, ensure:
```bash
# Run the test suite
./test-gateway.sh

# Test health endpoint
curl http://localhost:4000/health

# Test routing
curl -X POST http://localhost:4000/gateway/route \
  -H "Content-Type: application/json" \
  -d '{"prompt": "your test prompt"}'
```

### Adding New Models

To add support for a new model:

1. Update `config.json`:
```json
{
  "models": {
    "your-model:latest": {
      "role": "your_role",
      "tags": ["keyword1", "keyword2"],
      "priority": 2
    }
  }
}
```

2. Test the routing:
```bash
curl -X POST http://localhost:4000/gateway/route \
  -H "Content-Type: application/json" \
  -d '{"prompt": "prompt with your keywords"}'
```

### Adding New Features

1. Create a feature branch
2. Implement your feature
3. Add tests
4. Update documentation
5. Submit a pull request

## Project Structure

```
ollama-gateway/
├── main.py          # FastAPI application and endpoints
├── router.py        # Intelligent routing logic
├── config.json      # Model configuration
└── requirements.txt # Python dependencies
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### PR Checklist
- [ ] Code follows project style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Commit messages are clear and descriptive

## Reporting Issues

When reporting issues, please include:
- Gateway version
- Python version
- Ollama version
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs

## Questions?

Feel free to open an issue for questions or discussions.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
