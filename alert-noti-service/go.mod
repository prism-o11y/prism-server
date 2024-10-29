module github.com/prism-o11y/prism-server/alert-noti-service

go 1.23.0

require github.com/rs/zerolog v1.33.0

replace github.com/prism-o11y/prism-server/shared => ../shared

require (
	github.com/go-playground/locales v0.14.1 // indirect
	github.com/go-playground/universal-translator v0.18.1 // indirect
	github.com/klauspost/compress v1.15.9 // indirect
	github.com/leodido/go-urn v1.4.0 // indirect
	github.com/modern-go/concurrent v0.0.0-20180228061459-e0a39a4cb421 // indirect
	github.com/modern-go/reflect2 v1.0.2 // indirect
	github.com/pierrec/lz4/v4 v4.1.15 // indirect
	gopkg.in/alexcesaro/quotedprintable.v3 v3.0.0-20150716171945-2caba252f4dc // indirect
	gopkg.in/go-playground/assert.v1 v1.2.1 // indirect
)

require (
	github.com/go-chi/chi/v5 v5.1.0
	github.com/go-playground/validator v9.31.0+incompatible
	github.com/json-iterator/go v1.1.12
	github.com/mattn/go-colorable v0.1.13 // indirect
	github.com/mattn/go-isatty v0.0.20 // indirect
	github.com/segmentio/kafka-go v0.4.47
	github.com/sethvargo/go-envconfig v1.1.0
	golang.org/x/sys v0.25.0 // indirect
	gopkg.in/gomail.v2 v2.0.0-20160411212932-81ebce5c23df
)
