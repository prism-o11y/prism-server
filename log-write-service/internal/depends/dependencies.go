package depends

import (
	"context"

	elastic "github.com/prism-o11y/prism-server/shared/data/elastics"
	"github.com/prism-o11y/prism-server/shared/data/kafka"
	"github.com/rs/zerolog/log"

	"github.com/prism-o11y/prism-server/log-write-service/internal/collector"
	"github.com/prism-o11y/prism-server/log-write-service/internal/conf"
)

type Dependencies struct {
	Config          *conf.Config
	ConsManager     *kafka.ConsumerManager
	ProducerManager *kafka.ProducerManager
	ESClient        *elastic.Client
	LogHandler      *collector.Handler
}

func New() (*Dependencies, error) {
	cfg, err := conf.New()
	if err != nil {
		return nil, err
	}

	consManager := kafka.NewConsumerManager()
	producerManager := kafka.NewProducerManager()
	client, err := elastic.NewElasticClient(cfg.Databases.ESAddress, cfg.Databases.ESUsername, cfg.Databases.ESPassword)
	if err != nil {
		return nil, err
	}

	logRepo := collector.NewRepository(client)
	svc := collector.NewService(logRepo)
	logHandler := collector.NewHandler(svc, producerManager, consManager, cfg.Server.NodeID)
	return &Dependencies{
		Config:          cfg,
		ConsManager:     consManager,
		ProducerManager: producerManager,
		ESClient:        client,
		LogHandler:      logHandler,
	}, nil
}

func (d *Dependencies) Close(ctx context.Context) error {
	d.ConsManager.CloseAllConsumers(ctx)
	d.ProducerManager.CloseAllProducers()

	if err := d.ESClient.Close(); err != nil {
		log.Error().Err(err).Msg("Failed to close ES client")
	}
	return nil
}
