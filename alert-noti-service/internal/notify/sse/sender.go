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
	clientsMap, exists := es.CliManager.clients[clientID]
	es.CliManager.mu.RUnlock()

	if !exists || len(clientsMap) == 0 {
		return fmt.Errorf("no clients connected with client_id %s", clientID)
	}

	sendErrors := make([]error, 0)
	for connectionID, client := range clientsMap {
		err := client.SendEvent(uuid.New().String(), "alert", notification.Message)
		if err != nil {
			log.Error().Err(err).Str("client_id", clientID).Str("connection_id", connectionID).Msg("Failed to send event to client")
			sendErrors = append(sendErrors, err)
		}
	}

	if len(sendErrors) > 0 {
		return fmt.Errorf("failed to send events to some clients")
	}

	return nil
}

func (es *EventSender) Close() {
	es.CliManager.CloseAllClients()
}
