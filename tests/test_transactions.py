import pytest


@pytest.mark.asyncio
async def test_create_and_list_transaction(client):
    category_resp = await client.post("/categories/", json={"name": "Food"})
    category_id = category_resp.json()["id"]

    transaction_resp = await client.post(
        "/transactions/",
        json={"date": "2026-08-07",
              "amount": 250,
              "description": "Fruits",
              "category_id": category_id,},
    )
    assert transaction_resp.status_code == 201
    assert transaction_resp.json()["category"]["name"] == "Food"

    list_resp = await client.get("/transactions/")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1