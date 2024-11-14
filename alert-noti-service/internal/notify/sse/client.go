package sse

import "github.com/google/uuid"

type Client struct{
	ClientID uuid.UUID `json:"client_id"`
	
}

func NewClient() *Client {
	return &Client{}
}
