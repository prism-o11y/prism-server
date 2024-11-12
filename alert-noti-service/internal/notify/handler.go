package notify

import (
	"context"
	"time"

	"github.com/prism-o11y/prism-server/shared/data/kafka"
	"github.com/rs/zerolog/log"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/models"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/smtp"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/sse"
)

type Handler struct {
	eventSender *sse.EventSender
	emailSender *smtp.EmailSender
	consManager *kafka.ConsumerManager
}

func NewHandler(eventSender *sse.EventSender, emailSender *smtp.EmailSender, consManager *kafka.ConsumerManager) *Handler {
	return &Handler{
		eventSender: eventSender,
		emailSender: emailSender,
		consManager: consManager,
	}
}

func (h *Handler) StartConsumers(ctx context.Context, brokers []string, topics []string, groupIDs []string, partition int, timeout time.Duration) {
	for i, topic := range topics {
		err := h.consManager.AddConsumer(
			brokers,
			topic,
			groupIDs[i],
			partition,
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

	retries, backoff := 3, time.Second*2
	for i := 0; i < retries; i++ {
		if err := h.emailSender.SendEmail(request); err != nil {
			log.Warn().Err(err).Msgf("Retrying to send email (%d/%d)", i+1, retries)
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
