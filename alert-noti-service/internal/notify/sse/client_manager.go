package sse

import (
	"fmt"
	"sync"
	"time"

	"github.com/rs/zerolog/log"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/sse/lock"
)

type clientManager struct {
	clients  map[string]*Client
	distLock *lock.DistributedLock
	mu       sync.RWMutex
	addMu    sync.Mutex
}

func newClientManager(distLock *lock.DistributedLock) *clientManager {
	return &clientManager{
		clients:  make(map[string]*Client),
		distLock: distLock,
	}
}

func (cm *clientManager) AddClient(clientID, nodeID string, client *Client) error {
	cm.addMu.Lock()
	defer cm.addMu.Unlock()

	cm.mu.Lock()
	existingClient, exists := cm.clients[clientID]
	if exists {
		log.Warn().Str("client_id", clientID).Msg("Client already connected, removing old client")

		existingClient.Close()
		delete(cm.clients, clientID)

		err := cm.distLock.Release(clientID)
		if err != nil {
			log.Error().Err(err).Str("client_id", clientID).Msg("Failed to release lock for existing client")
			cm.mu.Unlock()
			return err
		}

		time.Sleep(50 * time.Millisecond)
	}
	cm.mu.Unlock()

	err := cm.distLock.Acquire(clientID, nodeID)
	if err != nil {
		if err == lock.ErrLockAlreadyHeld {
			return fmt.Errorf("client %s is already connected to another node", clientID)
		}
		return err
	}

	cm.mu.Lock()
	cm.clients[clientID] = client
	cm.mu.Unlock()

	go client.StartHeartbeat(5*time.Minute, cm.distLock)
	go client.WaitForDisconnection(cm)

	log.Info().Str("client_id", clientID).Msg("Client added successfully")
	return nil
}

func (cm *clientManager) HasClient(clientID string, nodeID string) (string, bool, error) {
	cm.mu.RLock()
	defer cm.mu.RUnlock()

	lockNodeID, err := cm.distLock.GetNodeForClient(clientID)
	if err != nil {
		if err == lock.ErrNoLockFound {
			log.Warn().Str("client_id", clientID).Msg("Client not connected to any node")
			return "", false, nil
		}
		log.Error().Err(err).Str("client_id", clientID).Msg("Failed to get node for client")
		return "", false, err
	}

	_, exists := cm.clients[clientID]
	return lockNodeID, exists && lockNodeID == nodeID, nil
}

func (cm *clientManager) GetClient(clientID string) (*Client, bool) {
	cm.mu.RLock()
	defer cm.mu.RUnlock()
	client, exists := cm.clients[clientID]
	return client, exists
}

func (cm *clientManager) GetNodeForClient(clientID string) (string, error) {
	return cm.distLock.GetNodeForClient(clientID)
}

func (cm *clientManager) RemoveClient(clientID string) error {
	cm.mu.Lock()
	client, exists := cm.clients[clientID]
	if !exists {
		cm.mu.Unlock()
		log.Error().Str("client_id", clientID).Msg("Client not found")
		return fmt.Errorf("client %s not found", clientID)
	}

	client.Close()
	delete(cm.clients, clientID)
	cm.mu.Unlock()

	err := cm.distLock.Release(clientID)
	if err != nil {
		log.Error().Err(err).Str("client_id", clientID).Msg("Failed to release lock for client")
		return err
	}

	log.Info().Str("client_id", clientID).Msg("Client removed successfully")
	return nil
}

func (cm *clientManager) DisconnectAllClients() {
	if len(cm.clients) == 0 {
		log.Info().Msg("No clients to disconnect")
		return
	}

	cm.mu.RLock()
	clientsCopy := make(map[string]*Client, len(cm.clients))
	for clientID, client := range cm.clients {
		clientsCopy[clientID] = client
	}
	cm.mu.RUnlock()

	for clientID, client := range clientsCopy {
		log.Info().Str("client_id", clientID).Msg("Disconnecting client during shutdown")
		client.Close()

		if err := cm.distLock.Release(clientID); err != nil {
			log.Error().Err(err).Str("client_id", clientID).Msg("Failed to release lock for client")
		} else {
			log.Info().Str("client_id", clientID).Msg("Lock released for client")
		}
	}
}
