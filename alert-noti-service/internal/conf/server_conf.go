package conf

type Server struct {
	Name           string `env:"NAME, required"`
	Address        string `env:"EMAIL_ADDR, required"`
	AllowOrigins   Tokens `env:"ALLOWED_ORIGINS, required"`
	AllowedHeaders Tokens `env:"ALLOWED_HEADERS, required"`
}
