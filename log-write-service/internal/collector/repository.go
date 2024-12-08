package collector

import (
	"bytes"
	"context"

	"github.com/elastic/go-elasticsearch/v8/esutil"
	elastic "github.com/prism-o11y/prism-server/shared/data/elastics"
	"github.com/rs/zerolog/log"
)

type repository struct {
	elasticClient *elastic.Client
}

func NewRepository(client *elastic.Client) *repository {
	return &repository{
		elasticClient: client,
	}
}

func (r *repository) InsertLog(data []byte) error {
	err := r.elasticClient.BulkIndexer.Add(
		context.Background(),
		esutil.BulkIndexerItem{
			Action: "index",
			Body:   bytes.NewReader(data),
			OnFailure: func(ctx context.Context, item esutil.BulkIndexerItem, res esutil.BulkIndexerResponseItem, err error) {
				if err != nil {
					log.Error().Err(err).Msg("Bulk indexer failure")
				} else {
					log.Error().Str("error", res.Error.Reason).Msg("Bulk indexer item failed")
				}
			},
		})
	if err != nil {
		log.Error().Err(err).Msg("Failed to insert log")
		return err
	}
	return nil
}
