package data

import (
	"fmt"
	"sync"

	"github.com/rs/zerolog/log"
)

type KafkaManager struct {
	cMap map[string]*KafkaConsumer
	mu   sync.RWMutex
}

func NewKafkaManager(brokers []string, topics []string, groupIDs []string) *KafkaManager {
	km := &KafkaManager{
		cMap: make(map[string]*KafkaConsumer),
	}
	km.addConsumers(brokers, topics, groupIDs)
	return km
}

func (m *KafkaManager) addConsumers(brokers []string, topics []string, groupIDs []string) {
	m.mu.Lock()
	defer m.mu.Unlock()

	for i, topic := range topics {
		if _, ok := m.cMap[topic]; ok {
			log.Warn().Str("topic", topic).Msg("Consumer already exists")
			continue
		}

		m.cMap[topic] = NewKafkaConsumer(brokers, topic, groupIDs[i])
		log.Info().Str("topic", topic).Msg("Added new Kafka consumer")
	}
}

func (m *KafkaManager) GetConsumer(topic string) (*KafkaConsumer, error) {
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

func (m *KafkaManager) Close() {
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
