package collector

import (
	"context"
	"fmt"
	"net/http"
	"time"

	"github.com/go-playground/validator"
	segmentioKafka "github.com/segmentio/kafka-go"

	jsoniter "github.com/json-iterator/go"
	"github.com/prism-o11y/prism-server/shared/data/kafka"
	"github.com/rs/zerolog/log"
)

type Handler struct {
	nodeID          int
	producerManager *kafka.ProducerManager
	consManager     *kafka.ConsumerManager
	logService      *service
}

func NewHandler(logService *service, producerManager *kafka.ProducerManager, consManager *kafka.ConsumerManager, nodeID int) *Handler {
	return &Handler{
		nodeID:          nodeID,
		producerManager: producerManager,
		consManager:     consManager,
		logService:      logService,
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
	logEntry := &LogEntry{}
	if err := jsoniter.Unmarshal(msg.Value, logEntry); err != nil {
		log.Error().Err(err).Msg("Failed to unmarshal log entry")
		return err
	}

	if err := validator.New().Struct(logEntry); err != nil {
		log.Error().Err(err).Msg("Invalid log entry")
		return err
	}

	if err := h.logService.WriteLog(msg.Value); err != nil {
		log.Error().Err(err).Msg("Failed to write log entry")
		return err
	}

	log.Info().Interface("log_entry", logEntry).Msg("Received log entry")
	return nil
}

func (h *Handler) HandleLogWrite(w http.ResponseWriter, r *http.Request) {
	logEntry := &LogEntry{}
	if err := jsoniter.NewDecoder(r.Body).Decode(logEntry); err != nil {
		log.Error().Err(err).Msg("Failed to decode log entry")
		http.Error(w, "Failed to decode log entry", http.StatusBadRequest)
		return
	}

	if err := validator.New().Struct(logEntry); err != nil {
		log.Error().Err(err).Msg("Invalid log entry")
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	data, err := jsoniter.Marshal(logEntry)
	if err != nil {
		log.Error().Err(err).Msg("Failed to marshal log entry")
		http.Error(w, "Failed to marshal log entry", http.StatusInternalServerError)
		return
	}

	key := []byte(fmt.Sprintf("%s-%s", logEntry.ClientID, logEntry.ConnectionID))
	if err := h.producerManager.Produce(kafka.LogWriteTopic, key, data); err != nil {
		log.Error().Err(err).Msg("Failed to produce log entry")
		http.Error(w, "Failed to produce log entry", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusAccepted)
	w.Write([]byte("Log entry accepted"))
}
