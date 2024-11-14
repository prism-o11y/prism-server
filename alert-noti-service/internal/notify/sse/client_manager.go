package sse

import (
	"sync"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/sse/lock"
)

type clientManager struct {
	clients  map[string]*Client
	distLock *lock.DistributedLock
	mu       sync.RWMutex
}

func newClientManager(distLock *lock.DistributedLock) *clientManager {
	return &clientManager{
		clients:  make(map[string]*Client),
		distLock: distLock,
	}
}
