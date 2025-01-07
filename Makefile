LAYER_HASH_FILE := $(PROJECT_ROOT)/.layer_hash

.PHONY: build-LambdasBusinessLogicLayer build-layer-hash

build-LambdasBusinessLogicLayer: 
	@echo "* Building the layer..."
	mkdir -p .layer
	cp -r src/business_logic .layer
	mkdir -p ${ARTIFACTS_DIR}/python/
	mv .layer/business_logic ${ARTIFACTS_DIR}/python/
	@echo "* Layer built successfully"


	@echo ""
	@echo "[-] Checking if the layer has changes..."

	@if [ -f $(LAYER_HASH_FILE) ]; then \
		OLD_HASH=$$(cat $(LAYER_HASH_FILE)); \
		NEW_HASH=$$(find .layer -type f -exec shasum {} + | shasum | awk '{ print $$1 }'); \
		echo "[-] Old hash: $$OLD_HASH"; \
		echo "[-] New hash: $$NEW_HASH"; \
		rm -rf .layer; \
		if [ "$$OLD_HASH" = "$$NEW_HASH" ]; then \
			echo "[!!] No changes detected in the layer. Skipping deployment..."; \
			exit 1; \
		else \
			echo "[!] The dependencies are different, generating a new hash "; \
			echo "[-] Generating layer hash..."; \
			echo $$NEW_HASH > $(LAYER_HASH_FILE); \
			if [ "$$(cat $(LAYER_HASH_FILE))" = "$$NEW_HASH" ]; then \
				echo "[-] Hash generated successfully"; \
			else \
				echo "[!!] Failed to write the new hash"; \
				exit 1; \
			fi; \
		fi; \
	fi


