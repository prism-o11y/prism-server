package conf

type Databases struct {
	KafkaAddress string `env:"KAFKA_ADDR, required"`
	ESAddress    string `env:"ELASTICSEARCH_ADDR, required"`
	ESUsername   string `env:"ELASTICSEARCH_USERNAME, required"`
	ESPassword   string `env:"ELASTICSEARCH_PASSWORD, required"`
}
