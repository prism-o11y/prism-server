package conf

type databases struct {
	KafkaAddress   string `env:"KAFKA_ADDR, required"`
	Topics         Tokens `env:"KAFKA_TOPICS, required"`
	ConsumerGroups Tokens `env:"KAFKA_CONSUMER_GROUPS, required"`
}
