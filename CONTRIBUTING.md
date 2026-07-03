# Contributing to Autonomous Legal Reasoning Engine

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

1. **Fork the Repository**
   - Fork the project to your GitHub account
   - Clone your fork locally

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Write clean, documented code
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd frontend
   npm test
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Describe your changes

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints
- Write docstrings for functions and classes
- Maximum line length: 100 characters

### TypeScript/React (Frontend)
- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Write meaningful component and variable names

## Reporting Issues

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python/Node version)
- Screenshots if applicable

## Feature Requests

We welcome feature requests! Please:
- Check if the feature already exists
- Clearly describe the feature and its benefits
- Provide examples or mockups if possible

## Questions?

Feel free to open an issue for questions or reach out to the maintainers.

Thank you for contributing!
