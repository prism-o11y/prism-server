package kafka

import (
	"context"
	"time"

	"github.com/segmentio/kafka-go"
)

type Consumer struct {
	reader  *kafka.Reader
	timeout time.Duration
}

func NewConsumer(brokers []string, topic string, groupID string, timeout time.Duration) *Consumer {
	return &Consumer{
		reader: kafka.NewReader(kafka.ReaderConfig{
			Brokers: brokers,
			Topic:   topic,
			GroupID: groupID,
		}),	
		timeout: timeout,
	}
}

func (k *Consumer) ReadMessage() ([]byte, error) {
	ctx, cancel := context.WithDeadline(context.Background(), time.Now().Add(k.timeout))
	defer cancel()

	msg, err := k.reader.ReadMessage(ctx)
	if err != nil {
		return nil, err
	}

	return msg.Value, nil
}
