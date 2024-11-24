package kafka

import (
	"context"
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

	m.cMap[topic] = NewConsumer(brokers, topic, groupID, partition, timeout, handler)
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

func (cm *ConsumerManager) CloseAllConsumers(ctx context.Context) {
	var wg sync.WaitGroup

	for topic, consumer := range cm.cMap {
		wg.Add(1)
		go func(c *Consumer, topic string) {
			defer wg.Done()
			log.Info().Msgf("Closing consumer for topic=%s", topic)
			if err := c.Close(); err != nil {
				log.Error().Err(err).Msgf("Error closing consumer topic=%s", topic)
			}
		}(consumer, topic)
	}

	done := make(chan struct{})
	go func() {
		wg.Wait()
		close(done)
	}()

	select {
	case <-done:
		log.Info().Msg("All consumers closed")
	case <-ctx.Done():
		log.Warn().Msg("Timeout waiting for consumers to close")
	}
}
