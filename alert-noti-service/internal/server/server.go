package server

import (
	"context"
	"net/http"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/rs/zerolog/log"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/depends"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify"
	"github.com/prism-o11y/prism-server/alert-noti-service/pkg/server"
)

type Server struct {
	emailHandler *notify.Handler
	router       *chi.Mux
	server       *http.Server
}

func New(deps *depends.Dependencies) (*Server, error) {
	consumer, err := deps.ConsManager.GetConsumer("notify-topic")
	if err != nil {
		return nil, err
	}

	handler := notify.NewHandler(deps.SMTPProvider, consumer)
	router := chi.NewRouter()

	s := &Server{
		emailHandler: handler,
		router:       router,
		server: &http.Server{
			Addr:    deps.Config.Server.Address,
			Handler: router,
		},
	}

	s.routes()

	return s, nil
}

func (s *Server) routes() {
	s.router.Get("/health", server.HealthCheckHandler)
}

func (s *Server) Start(ctx context.Context) {
	go s.emailHandler.Start(ctx)

	log.Info().Msg("Starting HTTP server")
	if err := s.server.ListenAndServe(); err != http.ErrServerClosed {
		log.Fatal().Err(err).Msg("HTTP server crashed")
	}
}

func (s *Server) Stop() error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := s.server.Shutdown(ctx); err != nil {
		log.Error().Err(err).Msg("Error shutting down HTTP server")
		return err
	}

	log.Info().Msg("HTTP server stopped")
	return nil
}
