package main

import (
	"os"
	"time"

	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/alert"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/depends"
)

func main() {
	logConfig := zerolog.ConsoleWriter{
		Out:        os.Stderr,
		TimeFormat: time.ANSIC,
	}
	log.Logger = log.Output(logConfig).With().Caller().Logger()

	deps, err := depends.New()
	if err != nil {
		log.Fatal().Err(err).Msg("failed to load config")
	}

	sampleData := &alert.Data{
		Recipient: "tuan882612@gmail.com",
		Severity:  alert.INFO,
		Message:   "This is a sample message",
		DateTime:  time.Now(),
	}

	provider := deps.SMTPProvider
	if err := provider.SendMail(sampleData); err != nil {
		log.Error().Err(err).Msg("failed to send email")
	}
}
