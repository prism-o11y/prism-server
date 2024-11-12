package kafka

import (
	"fmt"
	"sync"
	"time"

	"github.com/rs/zerolog/log"
)

type ConsumerManager struct {
	cMap map[string]*Consumer
	mu   sync.RWMutex
}

func NewConsumerManager() *ConsumerManager {
	return &ConsumerManager{
		cMap: make(map[string]*Consumer),
	}
}

func (m *ConsumerManager) AddConsumer(brokers []string, topic string, groupID string, partition int, timeout time.Duration, handler HandlerFunc) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	if _, exists := m.cMap[topic]; exists {
		log.Warn().Str("topic", topic).Msg("Consumer already exists, skipping")
		return fmt.Errorf("consumer already exists for topic %s", topic)
	}

	consumer := NewConsumer(brokers, topic, groupID, partition, timeout, handler)
	m.cMap[topic] = consumer
	log.Info().Str("topic", topic).Msg("New Kafka consumer added")
	return nil
}

func (m *ConsumerManager) GetConsumer(topic string) (*Consumer, error) {
	m.mu.RLock()
	defer m.mu.RUnlock()

	consumer, exists := m.cMap[topic]
	if !exists {
		log.Error().Str("topic", topic).Msg("Consumer not found")
		return nil, fmt.Errorf("consumer not found for topic %s", topic)
	}
	return consumer, nil
}

func (m *ConsumerManager) CloseAllConsumers() {
	m.mu.Lock()
	defer m.mu.Unlock()

	log.Info().Msg("Closing all Kafka consumers")

	for topic, consumer := range m.cMap {
		if err := consumer.Close(); err != nil {
			log.Error().Err(err).Str("topic", topic).Msg("Error closing Kafka consumer")
		} else {
			log.Info().Str("topic", topic).Msg("Kafka consumer closed")
		}
		delete(m.cMap, topic)
	}

	log.Info().Msg("All Kafka consumers closed successfully")
}
