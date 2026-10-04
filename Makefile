SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

PYTHON     ?= python3.13
REPO       := $(shell pwd)
APP_DIR    := $(HOME)/Library/Application Support/email-clipper
VENV       := $(APP_DIR)/venv
SCRIPT     := $(APP_DIR)/process-inbox.sh
PLIST      := $(HOME)/Library/LaunchAgents/local.obsidian-email-clipper.plist
LABEL      := local.obsidian-email-clipper
LEGACY_LBL := com.bryan.email-clipper
LEGACY_PL  := $(HOME)/Library/LaunchAgents/com.bryan.email-clipper.plist
INBOX      := $(HOME)/Obsidian Inbox
LOGS       := $(HOME)/Library/Logs

.PHONY: help install refresh reload uninstall status logs test dev

help:
	@echo "Targets:"
	@echo "  install    - first-time setup: venv, package install, script, plist, launchd bootstrap"
	@echo "  refresh    - re-install package into runtime venv after code changes"
	@echo "  reload     - bootout + bootstrap launchd agent (pick up plist changes)"
	@echo "  uninstall  - tear down: bootout agent, remove plist, remove app dir"
	@echo "  status     - show launchctl status"
	@echo "  logs       - tail email-clipper logs"
	@echo "  test       - run pytest in dev venv"
	@echo "  dev        - create local .venv with editable install for development"

install:
	@mkdir -p "$(APP_DIR)" "$(INBOX)" "$(LOGS)"
	@test -d "$(VENV)" || $(PYTHON) -m venv "$(VENV)"
	@"$(VENV)/bin/pip" install --quiet --upgrade pip
	@"$(VENV)/bin/pip" install --quiet --force-reinstall "$(REPO)"
	@cp scripts/process-inbox.sh "$(SCRIPT)"
	@chmod +x "$(SCRIPT)"
	@sed -e "s|@APP_DIR@|$(APP_DIR)|g" \
	     -e "s|@INBOX@|$(INBOX)|g" \
	     -e "s|@LOGS@|$(LOGS)|g" \
	     scripts/launchagent.plist.tmpl > "$(PLIST)"
	@launchctl bootout gui/$$(id -u)/$(LEGACY_LBL) 2>/dev/null || true
	@rm -f "$(LEGACY_PL)"
	@launchctl bootout gui/$$(id -u)/$(LABEL) 2>/dev/null || true
	@launchctl bootstrap gui/$$(id -u) "$(PLIST)"
	@launchctl list | grep $(LABEL) || true
	@echo "Installed. Drop .eml files into: $(INBOX)"

refresh:
	@test -d "$(VENV)" || { echo "Runtime venv missing; run 'make install' first."; exit 1; }
	@"$(VENV)/bin/pip" install --quiet --force-reinstall --no-deps "$(REPO)"
	@cp scripts/process-inbox.sh "$(SCRIPT)"
	@chmod +x "$(SCRIPT)"
	@echo "Runtime refreshed from $(REPO)"

reload:
	@launchctl bootout gui/$$(id -u)/$(LABEL) 2>/dev/null || true
	@launchctl bootstrap gui/$$(id -u) "$(PLIST)"
	@launchctl list | grep $(LABEL) || true

uninstall:
	@launchctl bootout gui/$$(id -u)/$(LEGACY_LBL) 2>/dev/null || true
	@rm -f "$(LEGACY_PL)"
	@launchctl bootout gui/$$(id -u)/$(LABEL) 2>/dev/null || true
	@rm -f "$(PLIST)"
	@rm -rf "$(APP_DIR)"
	@echo "Uninstalled. (Inbox at $(INBOX) and vault notes left untouched.)"

status:
	@launchctl print gui/$$(id -u)/$(LABEL) 2>&1 | grep -E "state|runs|last exit" || echo "Agent not loaded"

logs:
	@tail -n 30 "$(LOGS)/email-clipper.log" 2>/dev/null || echo "(no main log yet)"
	@echo "---"
	@tail -n 10 "$(LOGS)/email-clipper.err.log" 2>/dev/null || true

test: dev
	@.venv/bin/pytest

dev:
	@test -d .venv || $(PYTHON) -m venv .venv
	@.venv/bin/pip install --quiet --upgrade pip
	@.venv/bin/pip install --quiet -e ".[dev]"
