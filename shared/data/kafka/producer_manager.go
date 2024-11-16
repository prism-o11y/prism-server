package kafka

import (
	"context"
	"fmt"
	"sync"

	"github.com/rs/zerolog/log"
)

type ProducerManager struct {
	producers map[string]*Producer
	mu        sync.RWMutex
}

func NewProducerManager() *ProducerManager {
	return &ProducerManager{
		producers: make(map[string]*Producer),
	}
}

func (m *ProducerManager) AddProducer(brokers []string, topic string, partition int) *Producer {
	m.mu.Lock()
	defer m.mu.Unlock()

	if producer, exists := m.producers[topic]; exists {
		return producer
	}

	producer := NewProducer(brokers, topic, partition)
	m.producers[topic] = producer
	log.Info().Str("topic", topic).Msg("New Kafka producer created")
	return producer
}

func (m *ProducerManager) ProduceToPartition(topic string, partition int, key, message []byte) error {
	m.mu.RLock()
	producer, exists := m.producers[topic]
	m.mu.RUnlock()

	if !exists {
		return fmt.Errorf("no producer found for topic %s", topic)
	}
	return producer.Produce(context.Background(), partition, key, message)
}

func (m *ProducerManager) CloseAllProducers() {
	m.mu.Lock()
	defer m.mu.Unlock()

	log.Info().Msg("Closing all Kafka producers")
	for topic, producer := range m.producers {
		if err := producer.Close(); err != nil {
			log.Error().Err(err).Str("topic", topic).Msg("Error closing Kafka producer")
		} else {
			log.Info().Str("topic", topic).Msg("Kafka producer closed")
		}
	}
	log.Info().Msg("All Kafka producers closed")
}
