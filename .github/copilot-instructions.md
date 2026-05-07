# Project Copilot Instructions

## Overview
This repository hosts a GitHub Copilot agent for generating unit test cases from user stories.

## Testing Conventions
- Use the **Arrange → Act → Assert** pattern for all tests.
- Test file naming: `test_<module_name>.py` (Python), `<ModuleName>.test.ts` (TypeScript), `<ModuleName>Test.java` (Java).
- Test method naming: `test_<methodName>_<scenario>_<expectedResult>`
- Group related tests using describe blocks (JS/TS) or nested classes (Java/Python).
- Mock all external dependencies (APIs, databases, file systems).
- Aim for 80%+ code coverage.
- Include both positive and negative test cases for every function.

## User Story Format
User stories should include:
- **Story ID**: Unique identifier (e.g., US-101)
- **Title**: Brief description
- **Description**: Detailed requirement
- **Acceptance Criteria**: Specific, testable conditions
- **Priority**: High / Medium / Low

## Supported Languages & Frameworks
The agent can generate tests for:
- **Java**: JUnit 5 + Mockito
- **Python**: pytest + unittest.mock
- **TypeScript/JavaScript**: Jest
- **C#**: xUnit + Moq

Adapt the output to match the language detected in the repository.
