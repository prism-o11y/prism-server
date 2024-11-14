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
	redisClient   *redis.Client
	Config        *conf.Config
	ConsManager   *kafka.ConsumerManager
	NotifyHandler *notify.Handler
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
	cacheManager := lock.NewDistributedLock(client)
	eventSender := sse.NewEventSender(cacheManager)
	notifyHandler := notify.NewHandler(eventSender, emailSender, consManager)

	return &Dependencies{
		Config:        cfg,
		redisClient:   client,
		ConsManager:   consManager,
		NotifyHandler: notifyHandler,
	}, nil
}

func (d *Dependencies) Close(ctx context.Context) error {
	d.ConsManager.CloseAllConsumers()

	if err := d.redisClient.Close(); err != nil {
		log.Error().Err(err).Msg("Failed to close redis client")
		return err
	}

	return nil
}
