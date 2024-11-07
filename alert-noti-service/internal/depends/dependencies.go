package depends

import (
	"context"

	"github.com/prism-o11y/prism-server/shared/data/kafka"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/conf"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/smtp"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/sse"
)

type Dependencies struct {
	Config        *conf.Config
	EmailSender   *smtp.EmailSender
	EventSender   *sse.EventSender
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

	consManager := kafka.NewConsumerManager()
	eventSender := sse.NewEventSender()

	notifyHandler := notify.NewHandler(eventSender, emailSender, consManager)

	return &Dependencies{
		Config:        cfg,
		EmailSender:   emailSender,
		ConsManager:   consManager,
		NotifyHandler: notifyHandler,
	}, nil
}

func (d *Dependencies) Close(ctx context.Context) error {
	d.ConsManager.CloseAllConsumers()
	return nil
}
