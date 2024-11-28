package sse

import (
	"context"
	"fmt"
	"net/http"
	"sync"
	"time"

	"github.com/rs/zerolog/log"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/sse/lock"
)

type Client struct {
	ClientID     string
	LastEventID  string
	ConnectionID string

	ResponseWriter http.ResponseWriter
	Flusher        http.Flusher

	ConnectedAt time.Time
	Context     context.Context
	cancelFunc  context.CancelFunc

	DisconnectChan chan struct{}
	mu             sync.Mutex
	once           sync.Once
}

func NewClient(clientID string, w http.ResponseWriter, reqCtx context.Context) (*Client, error) {
	flusher, ok := w.(http.Flusher)
	if !ok {
		return nil, fmt.Errorf("streaming unsupported")
	}

	ctx, cancel := context.WithCancel(reqCtx)
	return &Client{
		ClientID:       clientID,
		ResponseWriter: w,
		Flusher:        flusher,
		DisconnectChan: make(chan struct{}),
		ConnectedAt:    time.Now(),
		Context:        ctx,
		cancelFunc:     cancel,
	}, nil
}

func (c *Client) SendEvent(eventID, eventType, data string) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	message := ""
	if eventID != "" {
		message += fmt.Sprintf("id: %s\n", eventID)
		c.LastEventID = eventID
	}
	if eventType != "" {
		message += fmt.Sprintf("event: %s\n", eventType)
	}
	message += fmt.Sprintf("data: %s\n\n", data)

	if c.ResponseWriter != nil && c.Flusher != nil {
		_, err := fmt.Fprintf(c.ResponseWriter, "%s", message)
		if err != nil {
			log.Error().Err(err).Str("client_id", c.ClientID).Msg("Failed to send event, disconnecting client")
			c.Close()
			return err
		}
		c.Flusher.Flush()
	}

	return nil
}

func (c *Client) WaitForDisconnection(cm *clientManager, clientID, connectionID string) {
	select {
	case <-c.DisconnectChan:
		cm.RemoveClient(clientID, connectionID)
	case <-c.Context.Done():
		cm.RemoveClient(clientID, connectionID)
	}
}

func (c *Client) Close() {
	c.once.Do(func() {
		c.cancelFunc()
		close(c.DisconnectChan)
	})
}

func (c *Client) StartHeartbeat(interval time.Duration) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			c.mu.Lock()
			_, err := fmt.Fprintf(c.ResponseWriter, ": keep-alive\n\n")
			if err != nil {
				c.mu.Unlock()
				log.Error().Err(err).Str("client_id", c.ClientID).Msg("Failed to send heartbeat, disconnecting client")
				c.Close()
				return
			}
			c.Flusher.Flush()
			c.mu.Unlock()
		case <-c.Context.Done():
			return
		}
	}
}

func (c *Client) StartRenewLock(interval time.Duration, lockCtx context.Context, lock *lock.DistributedLock) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			if err := lock.Renew(c.ClientID); err != nil {
				log.Error().Err(err).Str("client_id", c.ClientID).Msg("Failed to renew lock")
				return
			}
		case <-lockCtx.Done():
			log.Info().Str("client_id", c.ClientID).Msg("Lock renewal stopped")
			return
		}
	}
}
