from bson import ObjectId


# inserts market scanner into mongo database
def mongo_insert_market_scanner(client, req_id, display_name, scanner_details, tags):
    market_scanner_collection = client.IBKR_DB.market_scanners

    scanner_doc = {
        "req_id": req_id,
        "display_name": display_name,
        "scanner_details": scanner_details.__dict__,
        "tags": tags
    }

    inserted_id = market_scanner_collection.insert_one(scanner_doc).inserted_id
    print(f'Market Scanner with id {inserted_id} successfully inserted')

# removes market scanner from mongo database
def mongo_remove_market_scanner(client, req_id):
    market_scanner_collection = client.IBKR_DB.market_scanners

    deleted_id = market_scanner_collection.delete_one({"req_id": req_id})
    print(f'Market scanner with req id {deleted_id} successfully deleted')

# retrieves all market scanners in db
def mongo_fetch_scanners(client):
    market_scanner_collection = client.IBKR_DB.market_scanners

    market_scanners = market_scanner_collection.find({})
    return market_scanners

# retrieves market scanner matching req_id
def mongo_fetch_matching_scanner(client, req_id):
    market_scanner_collection = client.IBKR_DB.market_scanners

    market_scanner = market_scanner_collection.find_one({"req_id": req_id})
    return market_scanner

# finds display name of scanner from req id
def mongo_fetch_scanner_name(client, req_id):
    market_scanner_collection = client.IBKR_DB.market_scanners

    scanner_doc = market_scanner_collection.find_one({"req_id": req_id})
    scanner_name = scanner_doc.get("display_name")
    return scanner_name

# finds tags of scanner from req id
def mongo_fetch_scanner_tags(client, req_id):
    market_scanner_collection = client.IBKR_DB.market_scanners

    scanner_doc = market_scanner_collection.find_one({"req_id": req_id})
    scanner_tags = scanner_doc.get("tags")
    return scanner_tags