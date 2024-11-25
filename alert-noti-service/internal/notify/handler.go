package notify

import (
	"context"
	"fmt"
	"net/http"
	"time"

	jsoniter "github.com/json-iterator/go"
	"github.com/prism-o11y/prism-server/shared/data/kafka"
	"github.com/rs/zerolog/log"
	segmentioKafka "github.com/segmentio/kafka-go"

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
		nodeID:          nodeID + 1,
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
		if err := h.producerManager.AddProducer(brokers, topic); err != nil {
			log.Error().Err(err).Str("topic", topic).Msg("Failed to add producer")
			continue
		}
	}
	<-ctx.Done()
}

func (h *Handler) processMessage(msg segmentioKafka.Message) error {
	notification, err := models.ParseNotification(msg.Value)
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
	if clientID == "" {
		http.Error(w, "client_id is required", http.StatusBadRequest)
		return
	}

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

	connectionID, err := h.eventSender.CliManager.AddClient(clientID, fmt.Sprintf("%d", h.nodeID), client)
	if err != nil {
		if err.Error() == fmt.Sprintf("client %s is already connected to another node", clientID) {
			http.Error(w, "Client is connected to another node", http.StatusConflict)
			return
		}
		log.Error().Err(err).Msg("Failed to add client")
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	log.Info().Str("client_id", clientID).Str("connection_id", connectionID).Msg("SSE connection established")
	<-client.DisconnectChan
	log.Info().Str("client_id", clientID).Str("connection_id", connectionID).Msg("SSE connection closed")
}

func (h *Handler) handleSSENotification(notification *models.SSENotification) error {
	exists, err := h.eventSender.CliManager.HasClient(notification.ClientID, fmt.Sprintf("%d", h.nodeID))
	if err != nil {
		return err
	}
	if exists {
		return h.eventSender.SendEventToClient(notification.ClientID, notification)
	}
	return h.forwardMessageToNode(notification)
}

func (h *Handler) forwardMessageToNode(notification *models.SSENotification) error {
	nodeID, err := h.eventSender.CliManager.GetNodeForClient(notification.ClientID)
	if err != nil {
		log.Error().Err(err).Str("client_id", notification.ClientID).Msg("Failed to get node for client")
		return err
	}

	data, err := jsoniter.Marshal(notification)
	if err != nil {
		log.Err(err).Str("client_id", notification.ClientID).Msg("Failed to marshal notification data")
		return err
	}

	notifyData := models.NewNotificationWrapper(models.SSE, data)
	msg, err := jsoniter.Marshal(notifyData)
	if err != nil {
		log.Err(err).Str("client_id", notification.ClientID).Msg("Failed to marshal notification data")
		return err
	}

	key := []byte(fmt.Sprintf("%s:%s", nodeID, notification.ClientID))
	if err := h.producerManager.Produce(kafka.TransferTopic, key, msg); err != nil {
		return err
	}

	log.Info().Str("node_id", nodeID).Int("parent_id", h.nodeID).Msg("Message forwarded to node successfully")
	return nil
}

func (h *Handler) TestNotifyEndpoint(w http.ResponseWriter, r *http.Request) {
	notification := &models.SSENotification{}
	if err := jsoniter.NewDecoder(r.Body).Decode(notification); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}
	if err := h.handleSSENotification(notification); err != nil {
		http.Error(w, "Failed to handle notification", http.StatusInternalServerError)
		return
	}
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Notification processed"))
}
