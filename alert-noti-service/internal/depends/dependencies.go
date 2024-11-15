// alert-noti-service/internal/depends/dependencies.go

package depends

import (
	"context"

	"github.com/go-redis/redis"
	"github.com/prism-o11y/prism-server/shared/data/kafka"
	"github.com/prism-o11y/prism-server/shared/data/rconn"
	"github.com/rs/zerolog/log"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/conf"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/smtp"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/sse"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/sse/lock"
)

type Dependencies struct {
	redisClient     *redis.Client
	Config          *conf.Config
	ConsManager     *kafka.ConsumerManager
	ProducerManager *kafka.ProducerManager
	EventSender     *sse.EventSender
	NotifyHandler   *notify.Handler
}

func New() (*Dependencies, error) {
	cfg, err := conf.New()
	if err != nil {
		return nil, err
	}

	emailSender, err := smtp.NewEmailSender(cfg.Smtp)
	if err != nil {
		return nil, err
	}

	client, err := rconn.NewConnection(cfg.Databases.RedisURL, cfg.Databases.RedisPassword)
	if err != nil {
		return nil, err
	}

	consManager := kafka.NewConsumerManager()
	producerManager := kafka.NewProducerManager()

	cacheManager := lock.NewDistributedLock(client, lock.DefaultLockTTL)
	eventSender := sse.NewEventSender(cacheManager)
	nodeID := cfg.Server.NodeID
	notifyHandler := notify.NewHandler(eventSender, emailSender, producerManager, consManager, nodeID)

	return &Dependencies{
		Config:          cfg,
		redisClient:     client,
		ConsManager:     consManager,
		ProducerManager: producerManager,
		EventSender:     eventSender,
		NotifyHandler:   notifyHandler,
	}, nil
}

func (d *Dependencies) Close(ctx context.Context) error {
	d.ConsManager.CloseAllConsumers()
	d.ProducerManager.CloseAllProducers()
	d.EventSender.Close()

	if err := d.redisClient.Close(); err != nil {
		log.Error().Err(err).Msg("Failed to close redis client")
		return err
	}

	return nil
}
