package conf

type Databases struct {
	RedisURL      string `env:"REDIS_URL, required"`
	RedisPassword string `env:"REDIS_PSW, required"`
	KafkaAddress  string `env:"KAFKA_ADDR, required"`
}
