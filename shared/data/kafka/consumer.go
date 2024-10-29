package kafka

import (
	"context"
	"errors"
	"time"

	"github.com/rs/zerolog/log"
	"github.com/segmentio/kafka-go"
)

type Consumer struct {
    reader  *kafka.Reader
    timeout time.Duration
}

func NewConsumer(brokers []string, topic string, groupID string, timeout time.Duration) *Consumer {
    return &Consumer{
        reader: kafka.NewReader(kafka.ReaderConfig{
            Brokers:  brokers,
            Topic:    topic,
            GroupID:  groupID,
            MinBytes: 10e3,  // 10KB
            MaxBytes: 10e6,  // 10MB
        }),
        timeout: timeout,
    }
}

func (k *Consumer) ReadMessage() ([]byte, error) {
    ctx, cancel := context.WithTimeout(context.Background(), k.timeout)
    defer cancel()

    msg, err := k.reader.ReadMessage(ctx)
    if err != nil {
        if errors.Is(err, context.DeadlineExceeded) {
            log.Debug().Msg("No new messages in Kafka topic.")
        } else {
            log.Error().Err(err).Msg("Failed to read message from Kafka")
        }
        return nil, err
    }

    return msg.Value, nil
}

func (c *Consumer) Close() error {
	return c.reader.Close()
}
