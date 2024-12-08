# syntax=docker/dockerfile:1

ARG GO_VERSION=1.23.1
FROM --platform=$BUILDPLATFORM golang:${GO_VERSION} AS build

# Set the working directory
WORKDIR /src

# Copy the entire monorepo into the container
COPY . .

# Change directory to log-write-service
WORKDIR /src/log-write-service

# Download dependencies
RUN go mod download

# Build the application
ARG TARGETARCH
RUN CGO_ENABLED=0 GOARCH=$TARGETARCH go build -o /bin/server ./cmd/prism/main.go

FROM alpine:latest AS final

# Install any runtime dependencies
RUN --mount=type=cache,target=/var/cache/apk \
    apk --update add \
        ca-certificates \
        tzdata \
        && \
        update-ca-certificates

# Create a non-privileged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser
USER appuser

# Copy the executable from the build stage
COPY --from=build /bin/server /bin/

# Expose the port
EXPOSE 8100

# Set the entrypoint
ENTRYPOINT [ "/bin/server" ]
