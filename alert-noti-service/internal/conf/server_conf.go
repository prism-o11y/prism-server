package conf

type Server struct {
	Name           string `env:"NAME, required"`
	Address        string `env:"EMAIL_ADDR, required"`
	NodeID         string `env:"NODE, required"`
	NodeCount      int    `env:"NODE_COUNT, required"`
	AllowOrigins   Tokens `env:"ALLOWED_ORIGINS, required"`
	AllowedHeaders Tokens `env:"ALLOWED_HEADERS, required"`
}
