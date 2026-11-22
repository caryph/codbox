# UltraBox — local build/test helpers.
# Run `make` for the target list. Nothing here deploys or publishes.

PORT ?= 8090
NPX  ?= npx
SRC  := editor synth player global
STAMP := .build-stamp

.DEFAULT_GOAL := help
.PHONY: help check editor player synth all dev serve watch debug offline offline-html clean distclean stamp

help:
	@echo "make dev        - build editor bundle, then serve website/ on :$(PORT)"
	@echo "make editor     - build website/beepbox_editor[.min].js only (usual test loop)"
	@echo "make watch      - rebuild editor on every .ts change (ctrl-c to stop)"
	@echo "make check      - type-check editor, player, synth without emitting (fast)"
	@echo "make serve      - serve website/ with cache disabled"
	@echo "make debug      - build editor, then swap unminified bundle in as .min.js"
	@echo "make player     - build player bundle"
	@echo "make synth      - build standalone synth bundle"
	@echo "make all        - synth + player + editor (= npm run build)"
	@echo "make offline    - build electron/offline bundle into to_deploy/"
	@echo "make clean      - remove build/ and to_deploy/"
	@echo "make distclean  - also remove generated website/beepbox*.js(.map)"

# Type checking only. Catches errors before the bundle step.
check:
	$(NPX) tsc --noEmit -p tsconfig.json
	$(NPX) tsc --noEmit -p tsconfig_player.json
	$(NPX) tsc --noEmit -p tsconfig_synth_only.json

editor:
	bash ./compile_beepbox_editor.sh
	@touch $(STAMP)

player:
	bash ./compile_beepbox_player.sh

synth:
	bash ./compile_beepbox_synth.sh

all: synth player editor

# Main test flow: rebuild, serve, open the URL printed.
dev: editor serve

serve:
	python3 ./tools/serve.py website $(PORT)

# Poll loop (no entr/fswatch dependency). Plain reload in browser after each rebuild.
watch:
	@echo "watching $(SRC)/*.ts for changes (ctrl-c to stop)"
	@touch $(STAMP); \
	while true; do \
		changed=$$(find $(SRC) -name '*.ts' -newer $(STAMP) 2>/dev/null | head -1); \
		if [ -n "$$changed" ]; then \
			echo "--> $$changed"; \
			$(MAKE) --no-print-directory editor || echo "!! build failed, keeping old bundle"; \
			touch $(STAMP); \
		fi; \
		sleep 1; \
	done

# Unminified bundle under the .min.js name that index.html loads. Debuggable stack traces.
debug: editor
	bash ./debugify.sh

offline:
	bash ./compile_beepbox_offline.sh

offline-html:
	bash ./compile_beepbox_offline_html.sh

clean:
	rm -rf build to_deploy $(STAMP)

# Generated bundles are gitignored, so removing them is safe but slow to rebuild.
distclean: clean
	rm -f website/beepbox*.js website/beepbox*.js.map website/player/beepbox*.js*
