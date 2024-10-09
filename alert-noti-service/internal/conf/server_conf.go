package conf

type server struct {
	Address        string `env:"EMAIL_ADDR, required"`
	AllowOrigins   Tokens `env:"ALLOWED_ORIGINS, required"`
	AllowedHeaders Tokens `env:"ALLOWED_HEADERS, required"`
}
