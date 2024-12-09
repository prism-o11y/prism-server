package elastic

import (
	"context"
	"time"

	"github.com/elastic/go-elasticsearch/v8"
	"github.com/elastic/go-elasticsearch/v8/esutil"
	"github.com/rs/zerolog/log"
)

type Client struct {
	Client      *elasticsearch.Client
	BulkIndexer esutil.BulkIndexer
}

func NewElasticClient(address, username, password string) (*Client, error) {
	cfg := elasticsearch.Config{
		Addresses: []string{address},
		Username:  username,
		Password:  password,
	}

	es, err := elasticsearch.NewClient(cfg)
	if err != nil {
		return nil, err
	}

	if _, err := es.Ping(); err != nil {
		return nil, err
	}

	bulkIndexer, err := esutil.NewBulkIndexer(esutil.BulkIndexerConfig{
		Client:        es,
		NumWorkers:    4,
		FlushBytes:    5e+6,
		FlushInterval: 30 * time.Second,
	})
	if err != nil {
		return nil, err
	}

	log.Info().Msg("Elasticsearch client created")

	return &Client{
		Client:      es,
		BulkIndexer: bulkIndexer,
	}, nil
}

func (ec *Client) Close() error {
	return ec.BulkIndexer.Close(context.Background())
}
