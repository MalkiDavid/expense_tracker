import pytest

@pytest.mark.asyncio
async def test_create_category(client):
    category_resp = await client.post("/categories/", json={"name": "Grocery"})
    assert category_resp.status_code == 201
    assert category_resp.json()["name"] == "Grocery"
    assert category_resp.json()["id"] >= 1

@pytest.mark.asyncio
async def test_list_categories(client):
    await client.post("/categories/", json={"name": "Grocery"})
    await client.post("/categories/", json={"name": "Rent"})
    await client.post("/categories/", json={"name": "Transport"})

    list_resp = await client.get("/categories/")
    assert list_resp.status_code == 200

    names = [c["name"] for c in list_resp.json()]
    assert "Grocery" in names
    assert "Rent" in names
    assert "Transport" in names

@pytest.mark.asyncio
async def test_duplicate_category_name_rejected(client):
    first_response = await client.post("/categories/", json={"name": "Food"})
    assert first_response.status_code == 201

    second_response = await client.post("/categories/", json={"name": "Food"})
    assert second_response.status_code == 409