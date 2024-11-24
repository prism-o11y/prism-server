package lock

import (
	"fmt"
	"time"

	"github.com/go-redis/redis"
	"github.com/rs/zerolog/log"
)

const DefaultLockTTL = 2 * time.Minute

var (
	ErrLockAlreadyHeld = fmt.Errorf("lock already held")
	ErrNoLockFound     = fmt.Errorf("no lock found")

	ErrFailedToAcquireLock = fmt.Errorf("failed to acquire lock")
	ErrFailedToReleaseLock = fmt.Errorf("failed to release lock")
	ErrFailedToRenewLock   = fmt.Errorf("failed to renew lock")
	ErrFailedToGetNode     = fmt.Errorf("failed to get node")
)

type DistributedLock struct {
	client *redis.Client
	ttl    time.Duration
}

func NewDistributedLock(client *redis.Client, ttl time.Duration) *DistributedLock {
	return &DistributedLock{
		client: client,
		ttl:    ttl,
	}
}

func (d *DistributedLock) Acquire(clientID, nodeID string) error {
	key := d.getClientKey(clientID)

	ok, err := d.client.SetNX(key, nodeID, d.ttl).Result()
	if err != nil {
		log.Error().Err(err).Str("client_id", clientID).Msg("Failed to acquire lock")
		return ErrFailedToAcquireLock
	}
	if !ok {
		log.Warn().Str("client_id", clientID).Msg("Lock already held by another node")
		return ErrLockAlreadyHeld
	}

	log.Info().Str("client_id", clientID).Str("node_id", nodeID).Msg("Lock acquired")
	return nil
}

func (d *DistributedLock) Release(clientID string) error {
	key := d.getClientKey(clientID)

	_, err := d.client.Del(key).Result()
	if err != nil {
		log.Error().Err(err).Str("client_id", clientID).Msg("Failed to release lock")
		return ErrFailedToReleaseLock
	}

	log.Info().Str("client_id", clientID).Msg("Lock released")
	return nil
}

func (d *DistributedLock) Renew(clientID string) error {
	key := d.getClientKey(clientID)

	_, err := d.client.Expire(key, d.ttl).Result()
	if err != nil {
		log.Error().Err(err).Str("client_id", clientID).Msg("Failed to renew lock")
		return ErrFailedToRenewLock
	}

	log.Info().Str("client_id", clientID).Msg("Lock renewed successfully")
	return nil
}

func (d *DistributedLock) GetNodeForClient(clientID string) (string, error) {
	key := d.getClientKey(clientID)

	nodeID, err := d.client.Get(key).Result()
	if err == redis.Nil {
		log.Warn().Str("client_id", clientID).Msg("No lock found for client")
		return "", ErrNoLockFound
	}
	if err != nil {
		log.Error().Err(err).Str("client_id", clientID).Msg("Failed to get node for client")
		return "", ErrFailedToGetNode
	}

	return nodeID, nil
}

func (d *DistributedLock) GetRenewInterval() time.Duration {
	return d.ttl / 2
}

func (d *DistributedLock) getClientKey(clientID string) string {
	return fmt.Sprintf("client:%s", clientID)
}
