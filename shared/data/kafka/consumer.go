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

func NewConsumer(brokers []string, topic string, groupID string, partition int, timeout time.Duration, handler HandlerFunc) *Consumer {
	readerCfg := kafka.ReaderConfig{
		Brokers:     brokers,
		Topic:       topic,
		GroupID:     groupID,
		MinBytes:    10e3,
		MaxBytes:    10e6,
	}
	
	ctx, cancel := context.WithCancel(context.Background())
	consumer := &Consumer{
		reader:  kafka.NewReader(readerCfg),
		timeout: timeout,
		ctx:     ctx,
		cancel:  cancel,
		handler: handler,
	}

	go consumer.start()

	return consumer
}

func (c *Consumer) start() {
	defer func() {
		log.Info().Str("topic", c.reader.Config().Topic).Msg("Consumer stopped")
	}()

	for {
		msg, err := c.reader.FetchMessage(c.ctx)
		if err != nil {
			if errors.Is(err, context.Canceled) || errors.Is(err, context.DeadlineExceeded) {
				log.Info().Str("topic", c.reader.Config().Topic).Msg("Consumer context canceled or deadline exceeded")
				return
			}
			log.Error().Err(err).Str("topic", c.reader.Config().Topic).Msg("Failed to fetch message from Kafka")
			time.Sleep(1 * time.Second)
			continue
		}

		c.processMessage(msg)

		select {
		case <-c.ctx.Done():
			log.Info().Str("topic", c.reader.Config().Topic).Msg("Consumer context canceled")
			return
		default:
			continue
		}
	}
}

func (c *Consumer) processMessage(msg kafka.Message) {
	if err := c.handler(msg.Value); err != nil {
		log.Error().Err(err).Str("topic", c.reader.Config().Topic).Msg("Handler failed to process message")
	}
	if err := c.reader.CommitMessages(c.ctx, msg); err != nil {
		log.Error().Err(err).Str("topic", c.reader.Config().Topic).Msg("Failed to commit message")
	}
}

func (c *Consumer) Close() error {
	c.cancel()
	return c.reader.Close()
}
