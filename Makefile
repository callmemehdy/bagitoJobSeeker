.PHONY: help install test-email test-scraper test-linkedin check-status run clean login

# Default target
help:
	@echo ""
	@echo "  Job BagitoJobSeeker - Makefile Commands"
	@echo ""
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          Install dependencies and setup environment"
	@echo "  make login            Fresh LinkedIn login (regenerate cookies)"
	@echo ""
	@echo "Testing:"
	@echo "  make test-email       Test Gmail configuration"
	@echo "  make test-scraper     Test custom Seek scraper"
	@echo "  make test-linkedin    Test LinkedIn Selenium scraper"
	@echo ""
	@echo "Running:"
	@echo "  make run              Run the job application bot"
	@echo "  make run FIRST_NAME=YourName  Run with custom first name"
	@echo ""
	@echo "Monitoring:"
	@echo "  make check-status     Check application status"
	@echo "  make logs             View recent application logs"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            Clean up temporary files"
	@echo "  make reset-applied    Reset applied jobs tracker"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs             Open documentation directory"
	@echo ""
	@echo ""

# Install dependencies
install:
	@echo " Installing dependencies..."
	@uv sync
	@echo " Dependencies installed!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Copy .env.example to .env"
	@echo "2. Fill in your credentials in .env"
	@echo "3. Run: make test-email"

# Fresh LinkedIn login
login:
	@echo " Starting fresh LinkedIn login..."
	@echo "This will regenerate your LinkedIn cookies."
	@echo ""
	@uv run python3 fresh_login.py
	@echo ""
	@echo " Fresh cookies saved! You can now run the bot."

# Test email configuration
test-email:
	@echo " Testing Gmail configuration..."
	@uv run python3 test_email_config.py

# Test custom scraper
test-scraper:
	@echo " Testing custom multi-platform scraper..."
	@uv run python3 -c "import asyncio; from scrapers.multi_platform_scraper import MultiPlatformScraper; from common.utils import load_json_file; asyncio.run(MultiPlatformScraper(load_json_file('./config/run_config.json')).scrape())"

# Test LinkedIn Selenium scraper
test-linkedin:
	@echo " Testing LinkedIn Selenium scraper..."
	@uv run python3 test_linkedin_scraper.py

# Check application status
check-status:
	@echo " Checking application status..."
	@uv run python3 check_application_status.py

# Run the application
FIRST_NAME ?= $(shell bash -c 'read -p "Enter your first name: " name; echo $$name')
run:
	@if [ -z "$(FIRST_NAME)" ]; then \
		echo " Error: FIRST_NAME is required"; \
		echo "Usage: make run FIRST_NAME=YourName"; \
		exit 1; \
	fi
	@echo " Running job application bot..."
	@echo "   First Name: $(FIRST_NAME)"
	@uv run python3 main.py --first_name $(FIRST_NAME) --min_score 0.3

# Clean up
clean:
	@echo " Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo " Cleanup complete!"

# Reset applied jobs
reset-applied:
	@echo " Resetting applied jobs tracker..."
	@echo '{"jobs": {}, "email_history": {}}' > application_pipeline/application_materials/applied.json
	@echo " Applied jobs reset!"

# View logs (if you implement logging to file)
logs:
	@if [ -f "application.log" ]; then \
		tail -n 50 application.log; \
	else \
		echo "No log file found. Run the application first."; \
	fi

# Open docs
.PHONY: docs
docs:
	@echo " Documentation files:"
	@ls -1 docs/
	@echo ""
	@echo "Main documentation: README.md"
	@echo "Quick start: docs/QUICK_START.md"

# Development helpers
dev-setup: install
	@echo " Development setup complete!"
	@echo ""
	@echo "Recommended next steps:"
	@echo "1. Set up .env file with your credentials"
	@echo "2. Run: make test-email"
	@echo "3. Run: make run FIRST_NAME=YourName"

# Quick test (all tests)
test: test-email test-scraper test-linkedin
	@echo " All tests completed!"

push:
	@git add . && read -p "enter a commit message: " commit && git commit -m "$$commit" && git push