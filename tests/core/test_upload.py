from fastavro import parse_schema, writer
import io
import json

def test_record_serialization():
    schema_path = "media_analyzer/core/tweet.avsc"
    # schema_path = "tweet2.avsc"
    with open(schema_path) as f:
        schema = parse_schema(json.load(f))

    records_path = "tests/core/records.json"
    with open(records_path) as f:
        records = json.load(f)

    stream = io.BytesIO()
    for record in records:
        try:
            writer(stream, schema, [record], validator=True)
        except Exception as err:
            print(record)
            raise err

test_record_serialization()
