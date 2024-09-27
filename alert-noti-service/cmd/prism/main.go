package main

import (
	"os"
	"time"

	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
)

func main() {
	logConfig := zerolog.ConsoleWriter{
		Out:        os.Stderr,
		TimeFormat: time.ANSIC,
	}
	log.Logger = log.Output(logConfig).With().Caller().Logger()
	log.Info().Msg("Hello, World!")
}
