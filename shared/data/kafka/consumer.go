package kafka

import (
	"context"
	"errors"
	"time"

	"github.com/rs/zerolog/log"
	"github.com/segmentio/kafka-go"
)

type HandlerFunc func([]byte) error

type Consumer struct {
	reader  *kafka.Reader
	timeout time.Duration
	ctx     context.Context
	cancel  context.CancelFunc
	handler HandlerFunc
}

func NewConsumer(brokers []string, topic string, groupID string, timeout time.Duration, handler HandlerFunc) *Consumer {
	ctx, cancel := context.WithCancel(context.Background())
	reader := kafka.NewReader(kafka.ReaderConfig{
		Brokers:  brokers,
		Topic:    topic,
		GroupID:  groupID,
		MinBytes: 10e3,
		MaxBytes: 10e6,
	})

	consumer := &Consumer{
		reader:  reader,
		timeout: timeout,
		ctx:     ctx,
		cancel:  cancel,
		handler: handler,
	}

	go consumer.start()

	return consumer
}

func (c *Consumer) start() {
	for {
		select {
		case <-c.ctx.Done():
			log.Info().Str("topic", c.reader.Config().Topic).Msg("Consumer shutting down")
			return
		default:
			msg, err := c.reader.ReadMessage(c.ctx)
			if err != nil {
				if errors.Is(err, context.Canceled) {
					log.Info().Str("topic", c.reader.Config().Topic).Msg("Consumer context canceled")
					return
				}
				log.Error().Err(err).Str("topic", c.reader.Config().Topic).Msg("Failed to read message from Kafka")
				time.Sleep(1 * time.Second)
				continue
			}

			if err := c.handler(msg.Value); err != nil {
				log.Error().Err(err).Str("topic", c.reader.Config().Topic).Msg("Handler failed to process message")
			}
		}
	}
}

func (c *Consumer) Close() error {
	c.cancel()
	return c.reader.Close()
}
