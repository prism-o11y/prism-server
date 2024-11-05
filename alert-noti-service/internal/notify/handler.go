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
	emailSender *smtp.EmailSender
	manager     *kafka.ConsumerManager
}

func NewHandler(emailSender *smtp.EmailSender, manager *kafka.ConsumerManager) *Handler {
	return &Handler{
		emailSender: emailSender,
		manager:     manager,
	}
}

func (h *Handler) Start(ctx context.Context, brokers []string, topics []string, groupIDs []string, timeout time.Duration) {
	if len(topics) != len(groupIDs) {
		log.Fatal().Msg("The number of topics and groupIDs must match")
	}

	for i, topic := range topics {
		err := h.manager.AddConsumer(
			brokers,
			topic,
			groupIDs[i],
			timeout,
			func(msg []byte) error {
				return h.processMessage(msg)
			},
		)
		if err != nil {
			log.Error().Err(err).Str("topic", topic).Msg("Failed to add consumer")
			continue
		}
	}

	<-ctx.Done()
	log.Info().Msg("Handler shutdown initiated")
}

func (h *Handler) processMessage(msg []byte) error {
	request, err := models.ParseNotifyRequest(msg)
	if err != nil {
		return err
	}

	retryAttempts := 3
	backoff := time.Second * 2
	for i := 0; i < retryAttempts; i++ {
		if err := h.emailSender.SendMail(request); err != nil {
			log.Warn().Err(err).Msgf("Retrying to send email (%d/%d)", i+1, retryAttempts)
			time.Sleep(backoff)
			backoff *= 2
			continue
		}
		log.Info().Str("recipient", request.Recipient).Msg("Email sent successfully")
		return nil
	}

	log.Error().Err(err).Str("recipient", request.Recipient).Msg("Failed to send email after retries")
	return err
}
