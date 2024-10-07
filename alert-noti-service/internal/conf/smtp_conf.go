package conf

type smtp struct {
	Host     string `env:"HOST, required"`
	Port     int    `env:"PORT, required"`
	Email    string `env:"EMAIL, required"`
	Password string `env:"PASSWORD, required"`
}