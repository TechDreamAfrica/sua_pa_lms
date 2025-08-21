# Smart Campus System - Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview

This is a Django-based Smart Campus system for University of Central Technology (UCT) featuring:

- Learning Management System (LMS)
- Student Services Portal
- Administration Dashboard
- Mobile-responsive design with Tailwind CSS

## Code Standards

- Follow Django best practices and conventions
- Use class-based views where appropriate
- Implement proper authentication and authorization
- Use Tailwind CSS for styling
- Follow PEP 8 Python style guidelines
- Use proper Django model relationships
- Implement responsive design patterns

## Architecture Guidelines

- apps/: accounts, lms, student_services, administration
- Use Django's built-in User model with custom profile extensions
- Implement proper error handling and validation
- Use Django forms for data input
- Follow DRY (Don't Repeat Yourself) principles

## Security Considerations

- Always use Django's CSRF protection
- Implement proper user authentication
- Use Django's permission system
- Validate all user inputs
- Use secure session management
