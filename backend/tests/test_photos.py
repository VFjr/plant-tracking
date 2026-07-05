from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image


def make_test_jpeg(width: int = 2400, height: int = 1800) -> bytes:
    img = Image.new("RGB", (width, height), color=(120, 180, 90))
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def upload_test_photo(
    client: TestClient,
    plant_id: int,
    *,
    content: bytes | None = None,
    filename: str = "plant.jpg",
    content_type: str = "image/jpeg",
    caption: str | None = None,
    taken_at: str | None = None,
) -> dict:
    data: dict[str, tuple] = {
        "file": (filename, content or make_test_jpeg(), content_type),
    }
    if caption is not None:
        data["caption"] = (None, caption)
    if taken_at is not None:
        data["taken_at"] = (None, taken_at)

    response = client.post(f"/api/plants/{plant_id}/photos", files=data)
    assert response.status_code == 201
    return response.json()


def test_list_photos_empty(client: TestClient, plant: dict) -> None:
    response = client.get(f"/api/plants/{plant['id']}/photos")
    assert response.status_code == 200
    assert response.json() == []


def test_upload_and_list_photo(client: TestClient, plant: dict) -> None:
    photo = upload_test_photo(
        client,
        plant["id"],
        caption="New growth",
        taken_at="2026-07-01",
    )
    assert photo["filename"] == "plant.jpg"
    assert photo["stored_name"].endswith(".jpg")
    assert photo["caption"] == "New growth"
    assert photo["taken_at"] == "2026-07-01"

    response = client.get(f"/api/plants/{plant['id']}/photos")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_upload_resizes_large_image(client: TestClient, plant: dict) -> None:
    photo = upload_test_photo(client, plant["id"], content=make_test_jpeg(3200, 2400))

    file_response = client.get(f"/api/photos/{photo['id']}/file")
    assert file_response.status_code == 200
    assert file_response.headers["content-type"] == "image/jpeg"

    with Image.open(BytesIO(file_response.content)) as img:
        assert max(img.size) <= 1920


def test_serve_photo_file(client: TestClient, plant: dict) -> None:
    photo = upload_test_photo(client, plant["id"])
    response = client.get(f"/api/photos/{photo['id']}/file")
    assert response.status_code == 200
    assert len(response.content) > 0


def test_upload_rejects_invalid_type(client: TestClient, plant: dict) -> None:
    response = client.post(
        f"/api/plants/{plant['id']}/photos",
        files={"file": ("notes.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 422


def test_upload_rejects_empty_file(client: TestClient, plant: dict) -> None:
    response = client.post(
        f"/api/plants/{plant['id']}/photos",
        files={"file": ("empty.jpg", b"", "image/jpeg")},
    )
    assert response.status_code == 422


def test_upload_missing_plant(client: TestClient) -> None:
    response = client.post(
        "/api/plants/999/photos",
        files={"file": ("plant.jpg", make_test_jpeg(), "image/jpeg")},
    )
    assert response.status_code == 404


def test_delete_photo(client: TestClient, plant: dict) -> None:
    photo = upload_test_photo(client, plant["id"])

    response = client.delete(f"/api/photos/{photo['id']}")
    assert response.status_code == 204

    assert client.get(f"/api/plants/{plant['id']}/photos").json() == []
    assert client.get(f"/api/photos/{photo['id']}/file").status_code == 404


def test_delete_missing_photo(client: TestClient) -> None:
    response = client.delete("/api/photos/999")
    assert response.status_code == 404


def test_delete_plant_removes_photos(client: TestClient, plant: dict) -> None:
    photo = upload_test_photo(client, plant["id"])

    response = client.delete(f"/api/plants/{plant['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/photos/{photo['id']}/file").status_code == 404
