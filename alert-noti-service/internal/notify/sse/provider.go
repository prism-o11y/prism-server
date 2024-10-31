package sse

type Provider struct {
	cliManager *clientManager
}

func NewProvider() *Provider {
	manager := newClientManager()
	return &Provider{
		cliManager: manager,
	}
}
