package sse

type EventSender struct {
	cliManager *clientManager
}

func NewEventSender() *EventSender {
	return &EventSender{
		cliManager: newClientManager(),
	}
}
