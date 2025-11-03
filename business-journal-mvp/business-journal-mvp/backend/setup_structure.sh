#!/bin/bash
cd /home/claude/business-journal-mvp/backend
mkdir -p app/{api,core,models,schemas,services,prompts,utils}
mkdir -p app/api/routes
mkdir -p alembic/versions
mkdir -p tests
touch app/__init__.py
touch app/main.py
touch app/api/__init__.py
touch app/api/routes/__init__.py
touch app/core/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/services/__init__.py
touch app/prompts/__init__.py
touch app/utils/__init__.py
touch tests/__init__.py
echo "Backend structure created"
