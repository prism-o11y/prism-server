package kafka

import (
	"context"
	"sync"
	"time"

	"github.com/rs/zerolog/log"
	"github.com/segmentio/kafka-go"
)

type Producer struct {
	writer    *kafka.Writer
	partition int
	mu        sync.Mutex
	wg        sync.WaitGroup
}

func NewProducer(brokers []string, topic string, partition int) *Producer {
	return &Producer{
		writer: &kafka.Writer{
			Addr:     kafka.TCP(brokers...),
			Topic:    topic,
			Balancer: &kafka.Hash{},
		},
		partition: partition,
	}
}

func (p *Producer) Produce(ctx context.Context, partition int, key, message []byte) error {
	p.wg.Add(1)
	defer p.wg.Done()

	p.mu.Lock()
	defer p.mu.Unlock()

	msg := kafka.Message{
		Key:       key,
		Value:     message,
		Partition: partition,
		Time:      time.Now(),
	}

	if err := p.writer.WriteMessages(ctx, msg); err != nil {
		log.Error().Err(err).Msg("Failed to produce message")
		return err
	}
	log.Info().Msg("Message produced successfully")
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
