package server

import (
	"context"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/rs/zerolog/log"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/depends"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify"
	"github.com/prism-o11y/prism-server/alert-noti-service/pkg/server"
)

type Server struct {
	notifyHandler *notify.Handler
	deps          *depends.Dependencies
	router        *chi.Mux
	server        *http.Server
}

func New(deps *depends.Dependencies) (*Server, error) {
	address, err := buildAddress(deps.Config.Server.Address, deps.Config.Server.NodeID, deps.Config.Server.NodeCount)
	if err != nil {
		return nil, err
	}

	router := chi.NewRouter()
	s := &Server{
		deps:          deps,
		router:        router,
		server:        &http.Server{Addr: address, Handler: router},
		notifyHandler: notify.NewHandler(deps.SMTPEmailSender, deps.ConsManager),
	}
	s.routes()
	return s, nil
}

func buildAddress(address string, nodeID string, nodeCount int) (string, error) {
	parts := strings.Split(address, ":")
	if len(parts) < 2 {
		return "", fmt.Errorf("invalid server address format: %s", address)
	}

	host, port := parts[0], parts[1]
	if nodeCount > 1 {
		nodePort := fmt.Sprintf("%s%s", port[:len(port)-1], nodeID)
		return fmt.Sprintf("%s:%s", host, nodePort), nil
	}

	return address, nil
}

func (s *Server) routes() {
	s.router.Get("/health", server.HealthCheckHandler)
	s.router.Post("/event", func(w http.ResponseWriter, r *http.Request) {})
}

func (s *Server) Start(ctx context.Context) {
	brokers := []string{s.deps.Config.Databases.KafkaAddress}
	topics := []string{"notify-topic", "transfer-topic"}
	groups := []string{"notify-group", "transfer-group"}
	timeOut := 10 * time.Second
	go s.notifyHandler.Start(ctx, brokers, topics, groups, timeOut)

	log.Info().Str("address", s.server.Addr).Msgf("Starting HTTP server.")
	if err := s.server.ListenAndServe(); err != http.ErrServerClosed {
		log.Fatal().Err(err).Msg("HTTP server crashed")
	}
}

func (s *Server) Stop() error {
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()

	if err := s.server.Shutdown(ctx); err != nil {
		log.Error().Err(err).Msg("Error shutting down HTTP server")
		return err
	}

	log.Info().Msg("Closing all Kafka consumers")
	s.deps.ConsManager.CloseAllConsumers()

	log.Info().Msg("All consumers closed successfully")

	return nil
}
