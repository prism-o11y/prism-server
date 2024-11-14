package sse

import (
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/sse/lock"
)

type EventSender struct {
	cliManager *clientManager
}

func NewEventSender(cacheManager *lock.DistributedLock) *EventSender {
	return &EventSender{
		cliManager: newClientManager(cacheManager),
	}
}
