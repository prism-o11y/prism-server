package kafka

import (
	"context"
	"time"

	"github.com/rs/zerolog/log"
	"github.com/segmentio/kafka-go"
)

type Producer struct {
	writer    *kafka.Writer
	partition int
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
	return p.writer.Close()
}
