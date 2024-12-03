package sse

import (
	"fmt"

	"github.com/google/uuid"
	"github.com/rs/zerolog/log"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/models"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/sse/lock"
)

type EventSender struct {
	CliManager *clientManager
}

func NewEventSender(cacheManager *lock.DistributedLock) *EventSender {
	return &EventSender{
		CliManager: newClientManager(cacheManager),
	}
}

func (es *EventSender) SendEventToClient(clientID string, notification *models.SSENotification) error {
	es.CliManager.mu.RLock()
	ownerships, exists := es.CliManager.ownerships[clientID]
	es.CliManager.mu.RUnlock()

	if !exists || len(ownerships.connections) == 0 {
		return fmt.Errorf("no clients connected with client_id %s", clientID)
	}

	client := ownerships.connections[notification.ConnectionID]
	if client == nil {
		return fmt.Errorf("no client connected with connection_id %s", notification.ConnectionID)
	}

	if err := client.SendEvent(uuid.NewString(), string(models.SSE), notification.Message); err != nil {
		log.Error().Err(err).
			Str("client_id", clientID).
			Str("connection_id", notification.ConnectionID).
			Msg("Failed to send event to client")
		return err
	}

	log.Info().
		Str("client_id", notification.ClientID).
		Str("connection_id", notification.ConnectionID).
		Msg("Event sent to client successfully")
	return nil
}

func (es *EventSender) Close() {
	es.CliManager.CloseAllClients()
}
