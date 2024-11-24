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

func (m *ProducerManager) AddProducer(brokers []string, topic string) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	if _, exists := m.producers[topic]; exists {
		return fmt.Errorf("producer already exists for topic %s", topic)
	}

	m.producers[topic] = NewProducer(brokers, topic)
	log.Info().Str("topic", topic).Msg("New Kafka producer created")
	return nil
}

func (m *ProducerManager) Produce(topic string, key, message []byte) error {
	m.mu.RLock()
	producer, exists := m.producers[topic]
	m.mu.RUnlock()

	if !exists {
		return fmt.Errorf("no producer found for topic %s", topic)
	}
	return producer.Produce(context.Background(), key, message)
}

func (m *ProducerManager) CloseAllProducers() {
	m.mu.Lock()
	defer m.mu.Unlock()

	log.Info().Msg("Closing all Kafka producers")
	for topic, producer := range m.producers {
		if err := producer.Close(); err == nil {
			log.Info().Str("topic", topic).Msg("Kafka producer closed")
		}
	}
	log.Info().Msg("All Kafka producers closed")
}
