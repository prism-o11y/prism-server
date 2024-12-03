package depends

import (
	"context"

	"github.com/prism-o11y/prism-server/shared/data/kafka"

	"github.com/prism-o11y/prism-server/log-write-service/internal/conf"
)

type Dependencies struct {
	Config          *conf.Config
	ConsManager     *kafka.ConsumerManager
	ProducerManager *kafka.ProducerManager
}

func New() (*Dependencies, error) {
	cfg, err := conf.New()
	if err != nil {
		return nil, err
	}

	consManager := kafka.NewConsumerManager()
	producerManager := kafka.NewProducerManager()

	return &Dependencies{
		Config:          cfg,
		ConsManager:     consManager,
		ProducerManager: producerManager,
	}, nil
}

func (d *Dependencies) Close(ctx context.Context) error {
	d.ConsManager.CloseAllConsumers(ctx)
	d.ProducerManager.CloseAllProducers()

	return nil
}
