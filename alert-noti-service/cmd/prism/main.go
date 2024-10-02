package main

import (
	"os"
	"time"

	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"

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

	log.Info().Msg(deps.Config.Databases.Topics[0])
}
