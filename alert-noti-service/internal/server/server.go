package server

import (
	"context"
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/prism-o11y/prism-server/shared/data/kafka"
	"github.com/rs/zerolog/log"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/depends"
	"github.com/prism-o11y/prism-server/alert-noti-service/pkg/server"
)

type Server struct {
	deps   *depends.Dependencies
	router *chi.Mux
	server *http.Server
}

func New(deps *depends.Dependencies) (*Server, error) {
	svrCfg := deps.Config.Server
	address, err := buildAddress(svrCfg.Address, svrCfg.NodeID, svrCfg.NodeCount)
	if err != nil {
		return nil, err
	}

	router := chi.NewRouter()
	s := &Server{
		deps:   deps,
		router: router,
		server: &http.Server{Addr: address, Handler: router},
	}
	s.routes()
	return s, nil
}

func buildAddress(address string, nodeID int, nodeCount int) (string, error) {
	parts := strings.Split(address, ":")
	if len(parts) < 2 {
		return "", fmt.Errorf("invalid server address format: %s", address)
	}

	host, port := parts[0], parts[1]

	intPort, err := strconv.Atoi(port)
	if err != nil {
		log.Error().Err(err).Msgf("Failed to parse port '%s'", port)
		return "", err
	}

	if nodeCount > 1 {
		nodePort := fmt.Sprintf("%d", intPort+nodeID)
		return fmt.Sprintf("%s:%s", host, nodePort), nil
	}

	return address, nil
}

func (s *Server) routes() {
	s.router.Get("/health", server.HealthCheckHandler)
	s.router.Get("/events", s.deps.NotifyHandler.SSEHandler)
}

func (s *Server) Start(ctx context.Context) {
	brokers := []string{s.deps.Config.Databases.KafkaAddress}
	topics := []string{kafka.NotifyTopic, kafka.TransferTopic}
	groups := []string{kafka.NotifyGroupID, "temp-group"}
	timeOut := 10 * time.Second
	go s.deps.NotifyHandler.StartConsumers(ctx, brokers, topics, groups, timeOut)

	log.Info().Str("address", s.server.Addr).Msgf("Starting HTTP server.")
	if err := s.server.ListenAndServe(); err != http.ErrServerClosed {
		log.Fatal().Err(err).Msg("HTTP server crashed")
	}
}

func (s *Server) Stop() error {
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Minute)
	defer cancel()

	if err := s.server.Shutdown(ctx); err != nil {
		log.Error().Err(err).Msg("Error shutting down HTTP server")
		return err
	}
	s.deps.Close(ctx)
	return nil
}
