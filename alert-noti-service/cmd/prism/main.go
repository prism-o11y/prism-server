package main

import (
	"context"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/depends"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/server"
)

func setLogger() {
	level := zerolog.InfoLevel
	_, ok := os.LookupEnv("ENVIRONMENT")
	if ok {
		level = zerolog.DebugLevel
	}
	zerolog.SetGlobalLevel(level)

	logConfig := zerolog.ConsoleWriter{
		Out:        os.Stderr,
		TimeFormat: time.ANSIC,
	}
	log.Logger = log.Output(logConfig).With().Caller().Logger()
}

func main() {
	setLogger()

	deps, err := depends.New()
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to load dependencies")
	}

	srv, err := server.New(deps)
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to create server")
	}

	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	go srv.Start(ctx)

	<-ctx.Done()
	log.Info().Msg("Shutting down gracefully...")

	if err := srv.Stop(); err != nil {
		log.Fatal().Err(err).Msg("Failed to shut down server")
	}
	log.Info().Msg("Server stopped...")
}
