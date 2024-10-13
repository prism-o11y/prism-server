package email

import (
	"github.com/prism-o11y/prism-server/shared/data/kafka"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/email/smtp"
)

type service struct {
	smtpProvider  *smtp.Provider
	alertConsumer *kafka.Consumer
}

func newService(smtpProvider *smtp.Provider, alertConsumer *kafka.Consumer) *service {
	return &service{
		smtpProvider:  smtpProvider,
		alertConsumer: alertConsumer,
	}
}
