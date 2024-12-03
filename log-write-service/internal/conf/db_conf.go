package conf

type Databases struct {
	KafkaAddress  string `env:"KAFKA_ADDR, required"`
}
