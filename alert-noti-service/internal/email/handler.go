package email

import "github.com/rs/zerolog/log"

type Handler struct {
	emailSvc *service
}

func NewHandler(emailService *service) *Handler {
	return &Handler{
		emailSvc: emailService,
	}
}

func (h *Handler) Start() {
	for {
		if err := h.emailSvc.ConsumeEmail(); err != nil {
			log.Error().Err(err).Msg("Failed to send email")
		}

		log.Info().Msg("Email sent successfully")
	}
}
