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
	km := &ConsumerManager{
		cMap: make(map[string]*Consumer),
	}
	km.addConsumers(brokers, topics, groupIDs, timeout)
	return km
}

func (m *ConsumerManager) addConsumers(brokers []string, topics []string, groupIDs []string, timeout time.Duration) {
	m.mu.Lock()
	defer m.mu.Unlock()

	for i, topic := range topics {
		if _, ok := m.cMap[topic]; ok {
			log.Warn().Str("topic", topic).Msg("Consumer already exists")
			continue
		}

		m.cMap[topic] = NewConsumer(brokers, topic, groupIDs[i], timeout)
		log.Info().Str("topic", topic).Msg("Added new Kafka consumer")
	}
}

func (m *ConsumerManager) GetConsumer(topic string) (*Consumer, error) {
	m.mu.RLock()
	defer m.mu.RUnlock()

	if len(m.cMap) == 0 {
		log.Warn().Msg("No consumers found in Kafka manager.")
		return nil, fmt.Errorf("no consumers found in Kafka manager")
	}

	if _, ok := m.cMap[topic]; !ok {
		log.Error().Str("topic", topic).Msg("Consumer not found")
		return nil, fmt.Errorf("consumer not found for topic %s", topic)
	}

	return m.cMap[topic], nil
}

func (m *ConsumerManager) Close() {
	m.mu.Lock()
	defer m.mu.Unlock()

	for topic, c := range m.cMap {
		if _, ok := m.cMap[topic]; !ok {
			continue
		}

		if err := c.reader.Close(); err != nil {
			log.Error().Err(err).Str("topic", topic).Msg("Failed to close Kafka consumer")
			continue
		}

		log.Info().Str("topic", topic).Msg("Closed Kafka consumer")
	}
}
