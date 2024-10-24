package email

import (
	"github.com/prism-o11y/prism-server/shared/data"
	"github.com/prism-o11y/prism-server/shared/data/kafka"
	"github.com/rs/zerolog/log"

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

func (s *service) SendEmail() error {
	msg, err := s.alertConsumer.ReadMessage()
	if err != nil {
		return err
	}

	eventData, err := data.NewEventData(msg)
	if err != nil {
		return err
	}

	log.Info().Msgf("Sending email to %v", eventData.Email)

	return nil
}
