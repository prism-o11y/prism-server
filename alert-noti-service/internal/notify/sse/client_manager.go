package sse

import (
	"fmt"
	"sync"
	"time"

	"github.com/google/uuid"
	"github.com/rs/zerolog/log"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/sse/lock"
)

var (
	ErrAlreadyConnectedToAnotherNode = fmt.Errorf("client is already connected to another node")
)

type clientManager struct {
	clients  map[string]map[string]*Client
	distLock *lock.DistributedLock
	mu       sync.RWMutex
	addMu    sync.Mutex
}

func newClientManager(distLock *lock.DistributedLock) *clientManager {
	return &clientManager{
		clients:  make(map[string]map[string]*Client),
		distLock: distLock,
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
		err := cm.distLock.Acquire(clientID, nodeID)
		if err != nil {
			if err == lock.ErrLockAlreadyHeld {
				return "", fmt.Errorf("client %s is already connected to another node", clientID)
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

	if cm.clients[clientID] == nil {
		cm.clients[clientID] = make(map[string]*Client)
	}

	connectionID := uuid.New().String()
	client.ConnectionID = connectionID
	cm.clients[clientID][connectionID] = client

	log.Info().Str("client_id", clientID).Str("connection_id", connectionID).Msg("Client added successfully")

	go client.StartHeartbeat(5*time.Minute, cm.distLock)
	go client.WaitForDisconnection(cm, clientID, connectionID)

	return connectionID, nil
}

func (cm *clientManager) RemoveClient(clientID, connectionID string) error {
	cm.mu.Lock()
	defer cm.mu.Unlock()

	clientsMap, exists := cm.clients[clientID]
	if !exists {
		log.Warn().Str("client_id", clientID).Msg("Client ID not found during removal")
		return nil
	}

	client, exists := clientsMap[connectionID]
	if !exists {
		log.Warn().Str("client_id", clientID).Str("connection_id", connectionID).Msg("Connection ID not found during removal")
		return nil
	}

	client.Close()
	delete(clientsMap, connectionID)

	if len(clientsMap) == 0 {
		delete(cm.clients, clientID)
		err := cm.distLock.Release(clientID)
		if err != nil {
			log.Error().Err(err).Str("client_id", clientID).Msg("Failed to release lock after removing last client connection")
			return err
		}
		log.Info().Str("client_id", clientID).Msg("Released lock after last connection closed")
	}

	log.Info().Str("client_id", clientID).Str("connection_id", connectionID).Msg("Client removed successfully")
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

	exists := lockNodeID == nodeID && len(cm.clients[clientID]) > 0
	return exists, nil
}

func (cm *clientManager) GetNodeForClient(clientID string) (string, error) {
	return cm.distLock.GetNodeForClient(clientID)
}

func (cm *clientManager) CloseAllClients() {
	cm.mu.RLock()
	clientsCopy := make(map[string]map[string]*Client, len(cm.clients))
	for clientID, connections := range cm.clients {
		clientsCopy[clientID] = connections
	}
	cm.mu.RUnlock()

	for clientID, connections := range clientsCopy {
		for connectionID, client := range connections {
			log.Info().Str("client_id", clientID).Str("connection_id", connectionID).Msg("Closing client connection")
			client.Close()
		}
	}
}
