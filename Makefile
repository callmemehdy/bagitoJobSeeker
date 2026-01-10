.PHONY: help install test-email test-scraper test-linkedin check-status run clean login apply-offers test-one-offer

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
	@echo "  make test-one-offer   Test with just 1 job offer (ISMAIL, index 211)"
	@echo "  make test-scraper     Test custom Seek scraper"
	@echo "  make test-linkedin    Test LinkedIn Selenium scraper"
	@echo ""
	@echo "Running:"
	@echo "  make run              Run the job application bot"
	@echo "  make run FIRST_NAME=YourName  Run with custom first name"
	@echo "  make apply-offers     Apply to all jobs from offers file (auto-resume on error)"
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

# Apply to all jobs from offers file with auto-resume on error
OFFERS_FILE ?= offers_2025-11-10-10-57-35.json
MIN_SCORE ?= 0.0
OFFSET_FILE ?= offset.txt
DEFAULT_FIRST_NAME ?= ISMAIL
BATCH_SIZE ?= 20
START_INDEX ?= 200

# Test with just 1 job offer
test-one-offer:
	@echo " Testing with 1 job offer..."
	@echo "   First Name: $(DEFAULT_FIRST_NAME)"
	@echo "   Start Index: $(START_INDEX)"
	@echo "   Min Score: $(MIN_SCORE)"
	@. venv/bin/activate && python3 apply_from_offers.py \
		--offers_file $(OFFERS_FILE) \
		--first_name $(DEFAULT_FIRST_NAME) \
		--min_score $(MIN_SCORE) \
		--batch_size  \
		--start_index $(START_INDEX)

apply-offers:
	@if [ -z "$(FIRST_NAME)" ]; then \
		echo " Error: FIRST_NAME is required"; \
		echo "Usage: make apply-offers FIRST_NAME=YourName"; \
		echo ""; \
		echo "Optional parameters:"; \
		echo "  OFFERS_FILE=path/to/offers.json  (default: offers_2025-11-10-10-57-35.json)"; \
		echo "  MIN_SCORE=0.3                     (default: 0.0)"; \
		echo ""; \
		echo "Examples:"; \
		echo "  make apply-offers FIRST_NAME=John"; \
		echo "  make apply-offers FIRST_NAME=John MIN_SCORE=0.6"; \
		exit 1; \
	fi
	@START_INDEX=0; \
	if [ -f "$(OFFSET_FILE)" ]; then \
		START_INDEX=$$(cat $(OFFSET_FILE)); \
		echo " Resuming from offset $$START_INDEX"; \
	fi; \
	echo " Applying to all jobs from offers file..."; \
	echo "   First Name: $(FIRST_NAME)"; \
	echo "   Offers File: $(OFFERS_FILE)"; \
	echo "   Min Score: $(MIN_SCORE)"; \
	echo "   Start Index: $$START_INDEX"; \
	echo ""; \
	if uv run python3 apply_from_offers.py \
		--first_name $(FIRST_NAME) \
		--offers_file $(OFFERS_FILE) \
		--min_score $(MIN_SCORE) \
		--start_index $$START_INDEX \
		--offset_file $(OFFSET_FILE); then \
		rm -f $(OFFSET_FILE); \
		echo ""; \
		echo " All jobs processed successfully! Offset file removed."; \
	else \
		echo ""; \
		echo " Error occurred. Offset saved to $(OFFSET_FILE)"; \
		echo " Run 'make apply-offers FIRST_NAME=$(FIRST_NAME)' again to resume."; \
		exit 1; \
	fi

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