from media_analyzer.core import puller
from media_analyzer import apis


test_bucket_name = "media-analyzer-test"


def test_upload_avro():
    mock_tweets = [{"id": 123,
                    "publisher": "asdf",
                    "language": "qwer",
                    "created_at": "2018-12-04 00:20:06",
                    "text": "test text",
                    "tokens": ["as", "sd"],
                    "raw": "{}[]",
                   }]
    # puller.upload_avro(mock_tweets)
    resource = apis.get_aws()
    bucket = resource.Bucket(test_bucket_name)
    print(bucket.objects.all())
