package rconn

import (
	"github.com/go-redis/redis"
	"github.com/rs/zerolog/log"
)

func NewConnection(redisUrl, redisPsw string) (*redis.Client, error) {
	conn := redis.NewClient(&redis.Options{
		Addr:     redisUrl,
		Password: redisPsw,
		DB:       0,
	})

	_, err := conn.Ping().Result()
	if err != nil {
		log.Error().Err(err).Msg("failed to connect to redis")
		return nil, err
	}

	log.Info().Msg("Connected to redis.")
	return conn, nil
}
