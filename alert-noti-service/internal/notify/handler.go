package notify

import (
	"context"
	"time"

	"github.com/prism-o11y/prism-server/shared/data/kafka"
	"github.com/rs/zerolog/log"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/models"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/smtp"
)

type Handler struct {
	smtpProvider *smtp.Provider
	consumer     *kafka.Consumer
}

func NewHandler(smtpProvider *smtp.Provider, consumer *kafka.Consumer) *Handler {
	return &Handler{
		smtpProvider: smtpProvider,
		consumer:     consumer,
	}
}

func (h *Handler) Start(ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			log.Info().Msg("Handler shutdown initiated")
			return
		default:
			msg, err := h.consumer.ReadMessage()
			if err != nil {
				continue
			}

			if err := h.processMessage(msg); err != nil {
				log.Error().Err(err).Msg("Failed to process message")
			}
		}
	}
}

func (h *Handler) processMessage(msg []byte) error {
	request, err := models.ParseNotifyRequest(msg)
	if err != nil {
		return err
	}

	retryAttempts := 3
	for i := 0; i < retryAttempts; i++ {
		if err := h.smtpProvider.SendMail(request); err != nil {
			log.Warn().Err(err).Msgf("Retrying to send email (%d/%d)", i+1, retryAttempts)
			time.Sleep(time.Second * 2)
			continue
		}
		log.Info().Str("recipient", request.Recipient).Msg("Email sent successfully")
		return nil
	}

	return err
}
