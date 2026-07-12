import pytest

from utility import aws


@pytest.fixture
def mock_s3(mocker):
    """aws.s3 is constructed at import time (boto3.client('s3')), so patch the
    already-constructed object rather than the boto3.client constructor."""
    return mocker.patch.object(aws, "s3")


def test_upload_file_to_s3_calls_upload_fileobj(tmp_path, mock_s3):
    file_path = tmp_path / "skaters.parquet"
    file_path.write_bytes(b"fake parquet bytes")
    read_while_open = {}
    mock_s3.upload_fileobj.side_effect = lambda f, bucket, key: read_while_open.update(
        content=f.read(), bucket=bucket, key=key
    )

    aws.upload_file_to_s3(
        file_path=file_path, bucket_name="my-bucket", dest_object_name="moneypuck/skaters.parquet"
    )

    assert mock_s3.upload_fileobj.call_count == 1
    assert read_while_open == {
        "content": b"fake parquet bytes",
        "bucket": "my-bucket",
        "key": "moneypuck/skaters.parquet",
    }


def test_run_s3_upload_fileext_globs_and_builds_dest_path(tmp_path, mock_s3, mocker):
    nested = tmp_path / "raw" / "moneypuck" / "2023"
    nested.mkdir(parents=True)
    parquet_file = nested / "skaters.parquet"
    parquet_file.write_bytes(b"data")
    (nested / "notes.txt").write_text("ignore me")

    upload = mocker.patch.object(aws, "upload_file_to_s3")

    aws.run_s3_upload_fileext(data_dir=tmp_path, file_ext="parquet")

    upload.assert_called_once()
    call_kwargs = upload.call_args.kwargs
    assert call_kwargs["file_path"] == parquet_file
    assert call_kwargs["dest_object_name"] == "moneypuck/2023/skaters.parquet"


def test_run_s3_upload_fileext_respects_num_key_parts(tmp_path, mock_s3, mocker):
    nested = tmp_path / "raw" / "nhl_api" / "play_by_play" / "game_id=2024020003"
    nested.mkdir(parents=True)
    parquet_file = nested / "play_by_play.parquet"
    parquet_file.write_bytes(b"data")

    upload = mocker.patch.object(aws, "upload_file_to_s3")

    aws.run_s3_upload_fileext(data_dir=tmp_path, file_ext="parquet", num_key_parts=4)

    upload.assert_called_once()
    call_kwargs = upload.call_args.kwargs
    assert (
        call_kwargs["dest_object_name"]
        == "nhl_api/play_by_play/game_id=2024020003/play_by_play.parquet"
    )


def test_run_s3_upload_fileext_raises_when_no_matching_files(tmp_path):
    with pytest.raises(AssertionError, match="No files of type parquet found"):
        aws.run_s3_upload_fileext(data_dir=tmp_path, file_ext="parquet")


def test_module_import_requires_no_aws_credentials(monkeypatch):
    """Guards the assumption Task 9 depends on: boto3.client('s3') construction
    at import time must not require real credentials to succeed."""
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)

    import importlib

    importlib.reload(aws)
