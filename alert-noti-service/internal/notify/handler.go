package notify

import (
	"context"
	"fmt"
	"net/http"
	"strconv"
	"time"

	jsoniter "github.com/json-iterator/go"
	"github.com/prism-o11y/prism-server/shared/data/kafka"
	"github.com/rs/zerolog/log"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/models"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/smtp"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/sse"
)

type Handler struct {
	eventSender     *sse.EventSender
	emailSender     *smtp.EmailSender
	producerManager *kafka.ProducerManager
	consManager     *kafka.ConsumerManager
	nodeID          int
}

func NewHandler(eventSender *sse.EventSender, emailSender *smtp.EmailSender, producerManager *kafka.ProducerManager, consManager *kafka.ConsumerManager, nodeID int) *Handler {
	return &Handler{
		eventSender:     eventSender,
		emailSender:     emailSender,
		producerManager: producerManager,
		consManager:     consManager,
		nodeID:          nodeID,
	}
}

func (h *Handler) StartConsumers(ctx context.Context, brokers []string, topics []string, groupIDs []string, timeout time.Duration) {
	for i, topic := range topics {
		err := h.consManager.AddConsumer(
			brokers,
			topic,
			groupIDs[i],
			h.nodeID,
			timeout,
			h.processMessage,
		)
		if err != nil {
			log.Error().Err(err).Str("topic", topic).Msg("Failed to add consumer")
			continue
		}
	}
	<-ctx.Done()
}

func (h *Handler) processMessage(msg []byte) error {
	notification, err := models.ParseNotification(msg)
	if err != nil {
		return err
	}

	switch n := notification.(type) {
	case *models.SMTPNotification:
		return h.handleSMTPNotification(n)
	case *models.SSENotification:
		return h.handleSSENotification(n)
	default:
		return fmt.Errorf("unknown notification type")
	}
}

func (h *Handler) handleSMTPNotification(n *models.SMTPNotification) error {
	retries, backoff := 3, time.Second*2
	for i := 0; i < retries; i++ {
		if err := h.emailSender.SendEmail(n); err != nil {
			log.Warn().Err(err).Msgf("Retrying to send email (%d/%d)", i+1, retries)
			time.Sleep(backoff)
			backoff *= 2
			continue
		}

		log.Info().Str("recipient", n.Recipient).Msg("Email sent successfully")
		return nil
	}

	log.Error().Str("recipient", n.Recipient).Msg("Failed to send email after retries")
	return fmt.Errorf("failed to send email to %s", n.Recipient)
}

func (h *Handler) SSEHandler(w http.ResponseWriter, r *http.Request) {
	clientID := r.URL.Query().Get("client_id")
	nodeIDStr := fmt.Sprintf("%d", h.nodeID)

	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")

	w.Header().Set("Access-Control-Allow-Origin", "*")

	flusher, ok := w.(http.Flusher)
	if !ok {
		log.Error().Msg("Streaming unsupported")
		http.Error(w, "Streaming unsupported", http.StatusInternalServerError)
		return
	}

	flusher.Flush()

	client, err := sse.NewClient(clientID, w, r.Context())
	if err != nil {
		log.Error().Err(err).Msg("Failed to create client")
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	err = h.eventSender.CliManager.AddClient(clientID, nodeIDStr, client)
	if err != nil {
		if err.Error() == fmt.Sprintf("client %s is already connected to another node", clientID) {
			http.Error(w, "Client is connected to another node", http.StatusConflict)
			return
		}
		log.Error().Err(err).Msg("Failed to add client")
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	log.Info().Str("client_id", clientID).Msg("SSE connection established")

	<-client.DisconnectChan

	log.Info().Str("client_id", clientID).Msg("SSE connection closed")
}

func (h *Handler) handleSSENotification(n *models.SSENotification) error {
	clientID := n.ClientID
	nodeIDStr := fmt.Sprintf("%d", h.nodeID)

	lockNodeID, exist, err := h.eventSender.CliManager.HasClient(clientID, nodeIDStr)
	if err != nil {
		return err
	}

	if exist {
		if err := h.eventSender.SendEventToClient(clientID, n); err != nil {
			log.Error().Err(err).Str("client_id", clientID).Msg("Failed to send event to local client")
			return err
		}

		log.Info().Str("client_id", clientID).Msg("Event sent to client successfully")
		return nil
	} else {
		nodeID, err := h.eventSender.CliManager.GetNodeForClient(clientID)
		if err != nil {
			log.Error().Err(err).Str("client_id", clientID).Msg("Failed to get node for client")
			return err
		}

		if err = h.forwardMessageToNode(nodeID, lockNodeID, n); err != nil {
			log.Error().Err(err).Str("node_id", nodeID).Msg("Failed to forward message to node")
			return err
		}

		log.Info().Str("node_id", nodeID).Msg("Message forwarded to node successfully")
		return nil
	}
}

func (h *Handler) forwardMessageToNode(nodeID string, lockNodeID string, notification *models.SSENotification) error {
	msg, err := jsoniter.Marshal(notification)
	if err != nil {
		return err
	}

	lockIDInt, err := strconv.Atoi(lockNodeID)
	if err != nil {
		log.Err(err).Msg("Failed to convert lock node ID to int")
		return err
	}

	err = h.producerManager.ProduceToPartition(kafka.TransferTopic, lockIDInt, []byte(nodeID), msg)
	if err != nil {
		return err
	}

	return nil
}
