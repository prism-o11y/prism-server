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

func NewConsumerManager(brokers []string, topics []string, groupIDs []string, timeout time.Duration) *ConsumerManager {
	cm := &ConsumerManager{
		cMap: make(map[string]*Consumer),
	}
	cm.addConsumers(brokers, topics, groupIDs, timeout)
	return cm
}

func (m *ConsumerManager) addConsumers(brokers, topics, groupIDs []string, timeout time.Duration) {
	m.mu.Lock()
	defer m.mu.Unlock()

	for i, topic := range topics {
		if _, exists := m.cMap[topic]; exists {
			log.Warn().Str("topic", topic).Msg("Consumer already exists, skipping")
			continue
		}
		m.cMap[topic] = NewConsumer(brokers, topic, groupIDs[i], timeout)
		log.Info().Str("topic", topic).Msg("New Kafka consumer added")
	}
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

func (m *ConsumerManager) Close() {
	m.mu.Lock()
	defer m.mu.Unlock()

	for topic, consumer := range m.cMap {
		if err := consumer.Close(); err != nil {
			log.Error().Err(err).Str("topic", topic).Msg("Error closing Kafka consumer")
		} else {
			log.Info().Str("topic", topic).Msg("Kafka consumer closed")
		}
		delete(m.cMap, topic)
	}
}
