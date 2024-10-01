module github.com/prism-o11y/prism-server/alert-noti-service

go 1.23.1

require github.com/rs/zerolog v1.33.0

replace github.com/prism-o11y/prism-server/shared => ../../../shared

require (
	github.com/go-playground/locales v0.14.1 // indirect
	github.com/go-playground/universal-translator v0.18.1 // indirect
	github.com/leodido/go-urn v1.4.0 // indirect
)

require (
	github.com/go-playground/validator v9.31.0+incompatible
	github.com/joho/godotenv v1.5.1
	github.com/mattn/go-colorable v0.1.13 // indirect
	github.com/mattn/go-isatty v0.0.19 // indirect
	github.com/sethvargo/go-envconfig v1.1.0
	golang.org/x/sys v0.12.0 // indirect
)
