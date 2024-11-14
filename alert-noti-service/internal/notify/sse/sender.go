package sse

import (
	"fmt"

	"github.com/google/uuid"

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
	client, exists := es.CliManager.GetClient(clientID)
	if !exists {
		return fmt.Errorf("client %s not connected to this node", clientID)
	}

	data := notification.Message
	eventID := uuid.New().String()
	eventType := "alert"
	return client.SendEvent(eventID, eventType, data)
}
