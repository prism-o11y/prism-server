package kafka

import (
	"context"
	"sync"
	"time"

	"github.com/rs/zerolog/log"
	"github.com/segmentio/kafka-go"
)

type Producer struct {
	writer *kafka.Writer
	mu     sync.Mutex
	wg     sync.WaitGroup
}

func NewProducer(brokers []string, topic string) *Producer {
	return &Producer{
		writer: &kafka.Writer{
			Addr:  kafka.TCP(brokers...),
			Topic: topic,
			Balancer: &kafka.Murmur2Balancer{
				Consistent: true,
			},
		},
	}
}

func (p *Producer) Produce(ctx context.Context, key, message []byte) error {
	p.wg.Add(1)
	defer p.wg.Done()

	p.mu.Lock()
	defer p.mu.Unlock()

	msg := kafka.Message{
		Key:   key,
		Value: message,
		Time:  time.Now(),
	}

	if err := p.writer.WriteMessages(ctx, msg); err != nil {
		log.Error().Err(err).Msg("Failed to produce message")
		return err
	}
	return nil
}

func (p *Producer) Close() error {
	p.wg.Wait()
	p.mu.Lock()
	defer p.mu.Unlock()

	if err := p.writer.Close(); err != nil {
		log.Error().Err(err).Msg("Failed to close Kafka producer")
		return err
	}
	log.Info().Msg("Kafka producer closed successfully")
	return nil
}
