package sse

import (
	"context"
	"fmt"
	"sync"

	"github.com/google/uuid"
	"github.com/rs/zerolog/log"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/sse/lock"
)

type clientOwnership struct {
	connections map[string]*Client
	lockCtx     context.Context
	lockCancel  context.CancelFunc
}

type clientManager struct {
	ownerships map[string]*clientOwnership
	distLock   *lock.DistributedLock
	mu         sync.RWMutex
	addMu      sync.Mutex
}

func newClientManager(distLock *lock.DistributedLock) *clientManager {
	return &clientManager{
		ownerships: make(map[string]*clientOwnership),
		distLock:   distLock,
	}
}

func (cm *clientManager) AddClient(clientID, nodeID string, client *Client) (string, error) {
	cm.addMu.Lock()
	defer cm.addMu.Unlock()

	lockNodeID, err := cm.distLock.GetNodeForClient(clientID)
	if err != nil {
		if err != lock.ErrNoLockFound {
			return "", err
		}
		if err := cm.distLock.Acquire(clientID, nodeID); err != nil {
			if err == lock.ErrLockAlreadyHeld {
				return "", err
			}
			return "", err
		}
		lockNodeID = nodeID
	}

	if lockNodeID != nodeID {
		return "", fmt.Errorf("client %s is already connected to another node", clientID)
	}

	cm.mu.Lock()
	defer cm.mu.Unlock()

	lockInterval := cm.distLock.GetRenewInterval()

	if cm.ownerships[clientID] == nil {
		lockCtx, lockCancel := context.WithCancel(context.Background())
		cm.ownerships[clientID] = &clientOwnership{
			connections: make(map[string]*Client),
			lockCtx:     lockCtx,
			lockCancel:  lockCancel,
		}
		go client.StartRenewLock(lockInterval, lockCtx, cm.distLock)
	}

	connectionID := uuid.New().String()
	client.ConnectionID = connectionID
	cm.ownerships[clientID].connections[connectionID] = client

	go client.StartHeartbeat(lockInterval * 2)
	go client.WaitForDisconnection(cm, clientID, connectionID)

	return connectionID, nil
}

func (cm *clientManager) RemoveClient(clientID, connectionID string) error {
	cm.mu.Lock()
	defer cm.mu.Unlock()

	ownerships, exists := cm.ownerships[clientID]
	if !exists {
		log.Warn().Str("client_id", clientID).Msg("Client ID not found during removal")
		return nil
	}

	client, exists := ownerships.connections[connectionID]
	if !exists {
		log.Warn().
			Str("client_id", clientID).
			Str("connection_id", connectionID).
			Msg("Connection ID not found during removal")
		return nil
	}

	client.Close()
	delete(ownerships.connections, connectionID)

	if len(ownerships.connections) == 0 {
		ownerships.lockCancel()
		if err := cm.distLock.Release(clientID); err != nil {
			log.Error().Err(err).Str("client_id", clientID).Msg("Failed to release lock after removing last client connection")
			return err
		}
		log.Info().Str("client_id", clientID).Msg("No more client connections, lock released")
		delete(cm.ownerships, clientID)
	}

	return nil
}

func (cm *clientManager) HasClient(clientID string, nodeID string) (bool, error) {
	cm.mu.RLock()
	defer cm.mu.RUnlock()

	lockNodeID, err := cm.distLock.GetNodeForClient(clientID)
	if err != nil {
		if err == lock.ErrNoLockFound {
			log.Warn().Str("client_id", clientID).Msg("Client not connected to any node")
			return false, nil
		}
		log.Error().Err(err).Str("client_id", clientID).Msg("Failed to get node for client")
		return false, err
	}

	exists := lockNodeID == nodeID && len(cm.ownerships[clientID].connections) > 0
	return exists, nil
}

func (cm *clientManager) GetNodeForClient(clientID string) (string, error) {
	return cm.distLock.GetNodeForClient(clientID)
}

func (cm *clientManager) CloseAllClients() {
	cm.mu.RLock()
	ownershipsCopy := make(map[string]*clientOwnership, len(cm.ownerships))
	for clientID, connections := range cm.ownerships {
		ownershipsCopy[clientID] = connections
	}
	cm.mu.RUnlock()

	for clientID, ownerships := range ownershipsCopy {
		for connectionID, client := range ownerships.connections {
			log.Info().
				Str("client_id", clientID).
				Str("connection_id", connectionID).
				Msg("Closing client connection")
			client.Close()
		}
	}
}
