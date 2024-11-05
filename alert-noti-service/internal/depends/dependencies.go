package depends

import (
	"github.com/prism-o11y/prism-server/shared/data/kafka"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/conf"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/smtp"
)

type Dependencies struct {
	Config          *conf.Config
	SMTPEmailSender *smtp.EmailSender
	ConsManager     *kafka.ConsumerManager
}

func New() (*Dependencies, error) {
	conf, err := conf.New()
	if err != nil {
		return nil, err
	}

	tmplManager, err := smtp.NewTemplateManager()
	if err != nil {
		return nil, err
	}

	smtpEmailSender, err := smtp.NewEmailSender(conf.Smtp, tmplManager)
	if err != nil {
		return nil, err
	}

	consManager := kafka.NewConsumerManager()

	return &Dependencies{
		Config:          conf,
		SMTPEmailSender: smtpEmailSender,
		ConsManager:     consManager,
	}, nil
}
