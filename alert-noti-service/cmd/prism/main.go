package main

import (
	"os"
	"time"

	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/conf"
)

func main() {
	logConfig := zerolog.ConsoleWriter{
		Out:        os.Stderr,
		TimeFormat: time.ANSIC,
	}
	log.Logger = log.Output(logConfig).With().Caller().Logger()

	config, err := conf.New()
	if err != nil {
		log.Fatal().Err(err).Send()
	}

	log.Info().Msg(config.Server.Address)
}
