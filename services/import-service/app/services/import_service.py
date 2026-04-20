from enum import Enum
from fastapi import HTTPException, status
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from app.utils.enum_list import StatusEnum
from app.db.mongo import import_collection, scratch_card_issue_collection
from datetime import datetime
from datetime import datetime


    
class ImportService:

    async def save_data(self, records, user, store,upload_date):
        data = records

        # Ensure date exists
        if "date" not in data:
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Record is not valid"
            )

        # ✅ Check existing record for same store + date
        existing = await import_collection.find_one({
            "store": store,
            "date": data["date"]
        })

        if existing:
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Record already exists for this store and date"
            )

        # ✅ Add required fields
        data["store"] = store
        data["date"] = data["date"]
        data["upload_date"] = upload_date
        data["is_submitted"] = False
        data["status"] = StatusEnum.DRAFT.value  # Default status
        data["created_by"] = user

        # ✅ Get last submitted record
        lastday_data = await import_collection.find_one(
            {"store": store, "is_submitted": True},
            sort=[("date", -1)]
        )

        # ✅ Insert new record
        result = await import_collection.insert_one(data)

        inserted_data = await import_collection.find_one({
            "_id": result.inserted_id
        })

        inserted_data["_id"] = str(inserted_data["_id"])

        # ✅ Carry forward scratch card data
        scratch_card_data = (
            lastday_data.get('groups', {}).get('scratch_card_data')
            if lastday_data else None
        )

        if scratch_card_data:
            updated = [
                {
                    **item,
                    "open": item.get("close", 0) + item.get("issue", 0),
                    "close": 0,
                    "issue": 0,
                    "sales": 0,
                    "amount": 0,
                    "ref": None
                }
                for item in scratch_card_data
            ]

            inserted_data.setdefault('groups', {})
            inserted_data['groups']['scratch_card_data'] = updated

            # Optional: persist updated groups back to DB
            await import_collection.update_one(
                {"_id": result.inserted_id},
                {"$set": {"groups": inserted_data["groups"]}}
            )

        return inserted_data
    
    async def update_data(self, id, data):
        data.pop("_id", None)

        issue_records = []

        # ✅ Handle scratch card cleanup + extract issues
        if "scratch_card_data" in data.get('groups', {}):
            cleaned_data = []

            for item in data['groups']["scratch_card_data"]:
                if not item.get("name"):
                    continue

                cleaned_data.append(item)

                # ✅ Collect issue items
                if item.get("issue", 0) > 0:
                    issue_records.append({
                        "name": item.get("name"),
                        "date": data.get("date"),
                        "store": data.get("store"),
                        "price": item.get("price"),
                        "issue": item.get("issue"),
                        "ref": item.get("ref"),
                        "created_at": datetime.utcnow()
                    })

            data['groups']["scratch_card_data"] = cleaned_data

        # ✅ Mark as submitted
        data['is_submitted'] = True

        # ✅ Status based on difference
        daily_finance = data.get("groups", {}).get("daily_finance_data", {})
        difference = daily_finance.get("difference", 0)

        if difference > 0:
            data["status"] = "Submitted"
        else:
            data["status"] = "AutoApproved"

        # ✅ Update main document
        result = await import_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )

        if result.matched_count == 0:
            return {"message": "Document not found"}

        # ✅ 🔥 Store issues as ARRAY in another collection
        if issue_records:
            issue_doc = {
                "store": data.get("store"),
                "date": data.get("date"),
                "items": issue_records,   # 👈 array stored here
                "created_at": datetime.utcnow()
            }

            await scratch_card_issue_collection.insert_one(issue_doc)

        return {
            "message": "Updated successfully",
            "status": data["status"],
            "issues_count": len(issue_records)
        }
    
    async def approve_data(self, id: str, comment: str, user: dict):
        # Find the document by ID
        document = await import_collection.find_one({"_id": ObjectId(id)})

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Update the document's status to 'approved' and add the comment
        update_data = {
            "status": "Approved",
            "approved_by": user,
            "approved_at": datetime.utcnow(),
            "approval_comment": comment
        }

        result = await import_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to update document"
            )

        return {
            "message": "Document approved successfully",
            "id": id,
            "status": "Approved"
        }
    
    async def get(self, id):
        data = await import_collection.find_one({'_id':ObjectId(id)})
        if data:
            data["_id"] = str(data["_id"])
        return data


    async def list(self, filter):
        pipeline = []

        match_stage = {}

        if filter.store:
            match_stage["store"] = filter.store

        if filter.status:
            if isinstance(filter.status, list):
                match_stage["status"] = {"$in": filter.status}
            else:
                match_stage["status"] = filter.status

        # ✅ Convert string date → actual date
        pipeline.append({
            "$addFields": {
                "parsedDate": {
                    "$dateFromString": {
                        "dateString": "$date",
                        "format": "%d/%m/%Y %H:%M:%S"
                    }
                }
            }
        })

        # ✅ Apply date filter on parsedDate
        if filter.from_date or filter.to_date:
            date_filter = {}

            if filter.from_date:
                date_filter["$gte"] = datetime.combine(filter.from_date, datetime.min.time())

            if filter.to_date:
                date_filter["$lte"] = datetime.combine(filter.to_date, datetime.max.time())

            match_stage["parsedDate"] = date_filter

        pipeline.append({"$match": match_stage})

        # ✅ Sorting
        pipeline.append({"$sort": {"parsedDate": -1}})

        # ✅ Pagination
        skip = (filter.page - 1) * filter.limit
        pipeline.append({"$skip": skip})
        pipeline.append({"$limit": filter.limit})

        # ✅ Execute
        cursor = import_collection.aggregate(pipeline)

        data = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            data.append(doc)

        # ✅ Count (separate pipeline)
        count_pipeline = pipeline[:-2] + [{"$count": "total"}]
        count_result = await import_collection.aggregate(count_pipeline).to_list(1)
        total = count_result[0]["total"] if count_result else 0

        return {
            "items": data,
            "total": total,
            "page": filter.page,
            "limit": filter.limit
        }
