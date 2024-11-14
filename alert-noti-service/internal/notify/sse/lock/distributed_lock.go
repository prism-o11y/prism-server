package lock

import "github.com/go-redis/redis"

type DistributedLock struct {
	client *redis.Client
}

func NewDistributedLock(client *redis.Client) *DistributedLock {
	return &DistributedLock{
		client: client,
	}
}
