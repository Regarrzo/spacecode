WASI_SDK_PLATFORM := x86_64-linux
WASI_SDK_VERSION := 27.0
WASI_SDK_RELEASE := wasi-sdk-$(WASI_SDK_VERSION)-$(WASI_SDK_PLATFORM)
WASI_SDK_TARBALL := $(WASI_SDK_RELEASE)-$(WASI_SDK_PLATFORM).tar.gz 
WASI_SDK_URL := https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-$(WASI_SDK_VERSION)/$(WASI_SDK_TARBALL)
WASI_SDK_DIR := wasi-sdk

CC := $(WASI_SDK_DIR)/bin/clang
CFLAGS := --target=wasm32-wasi -Os
TARGET := simple_rammer.wasm
SRC := simple_rammer.c

all: $(TARGET)

$(TARGET): $(WASI_SDK_DIR) $(SRC)
	@echo "Building target: $(TARGET)"
	$(CC) $(CFLAGS) $(SRC) -o $(TARGET)
	@echo "Finished building target: $(TARGET)"

$(WASI_SDK_DIR):
	@if [ ! -d "$(WASI_SDK_DIR)" ]; then \
		echo "WASI SDK not found. Download and set it up? [Y/n] "; \
		read -r response; \
		case "$$response" in \
			[yY][eE][sS]|[yY]) \
				echo "Downloading WASI SDK..."; \
				wget -q --show-progress $(WASI_SDK_URL); \
				echo "Extracting WASI SDK..."; \
				tar -xzf $(WASI_SDK_TARBALL); \
				echo "Renaming WASI SDK directory..."; \
				mv $(WASI_SDK_RELEASE) $(WASI_SDK_DIR); \
				echo "Cleaning up..."; \
				rm $(WASI_SDK_TARBALL); \
				echo "WASI SDK setup complete.";; \
			*) \
				echo "Aborting."; \
				exit 1;; \
		esac \
	fi

clean:
	@echo "Cleaning up..."
	rm -f $(TARGET)

.PHONY: all clean $(WASI_SDK_DIR)