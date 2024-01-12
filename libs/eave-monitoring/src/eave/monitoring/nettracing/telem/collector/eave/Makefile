BINNAME = eave-collector

.PHONY: all
all:
	@echo "No default command rn"

.PHONY: install
install:
	go mod tidy

.PHONY: test
test:
	go test -v ./...

.PHONY: build
build:
	go build -o $(BINNAME)

.PHONY: run
run:
	make build && ./$(BINNAME) --config config.yaml
